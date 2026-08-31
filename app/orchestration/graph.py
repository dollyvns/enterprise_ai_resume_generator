import logging

from langgraph.graph import END, START, StateGraph

from app.agents.ats_optimizer import ATSOptimizationAgent
from app.agents.profile_analyzer import ProfileAnalyzerAgent
from app.agents.resume_writer import ResumeWriterAgent
from app.agents.reviewer import ReviewerAgent
from app.core.config import Settings
from app.models.outputs import ResumeGenerateResponse
from app.models.profile import ResumeGenerateRequest
from app.orchestration.state import ResumeState
from app.services.llm import StructuredLLM

logger = logging.getLogger("app.orchestrator")


class ResumeOrchestrator:
    def __init__(self, llm: StructuredLLM, settings: Settings):
        self.settings = settings
        self.profile_agent = ProfileAnalyzerAgent(llm)
        self.ats_agent = ATSOptimizationAgent(llm)
        self.writer_agent = ResumeWriterAgent(llm)
        self.reviewer_agent = ReviewerAgent(llm)
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(ResumeState)

        builder.add_node("profile_analyzer", self._profile_analyzer_node)
        builder.add_node("ats_optimizer", self._ats_optimizer_node)
        builder.add_node("resume_writer", self._resume_writer_node)
        builder.add_node("reviewer", self._reviewer_node)
        builder.add_node("revise_resume", self._revise_resume_node)

        builder.add_edge(START, "profile_analyzer")
        builder.add_edge("profile_analyzer", "ats_optimizer")
        builder.add_edge("ats_optimizer", "resume_writer")
        builder.add_edge("resume_writer", "reviewer")

        builder.add_conditional_edges(
            "reviewer",
            self._route_after_review,
            {
                "revise": "revise_resume",
                "finish": END,
            },
        )

        builder.add_edge("revise_resume", "reviewer")

        return builder.compile()

    async def _profile_analyzer_node(self, state: ResumeState) -> dict:
        result = await self.profile_agent.run(profile=state["profile"])
        return {"profile_analysis": result}

    async def _ats_optimizer_node(self, state: ResumeState) -> dict:
        result = await self.ats_agent.run(
            profile=state["profile"],
            analysis=state["profile_analysis"],
        )
        return {"ats_optimization": result}

    async def _resume_writer_node(self, state: ResumeState) -> dict:
        result = await self.writer_agent.run(
            profile=state["profile"],
            analysis=state["profile_analysis"],
            ats=state["ats_optimization"],
        )
        return {"resume": result, "revision_count": 0}

    async def _reviewer_node(self, state: ResumeState) -> dict:
        result = await self.reviewer_agent.run(
            profile=state["profile"],
            analysis=state["profile_analysis"],
            ats=state["ats_optimization"],
            resume=state["resume"],
        )
        return {"review": result}

    async def _revise_resume_node(self, state: ResumeState) -> dict:
        current_count = state.get("revision_count", 0)
        result = await self.writer_agent.revise(
            profile=state["profile"],
            analysis=state["profile_analysis"],
            ats=state["ats_optimization"],
            current_resume=state["resume"],
            revision_instructions=state["review"].revision_instructions,
        )
        return {
            "resume": result,
            "revision_count": current_count + 1,
        }

    def _route_after_review(self, state: ResumeState) -> str:
        review = state["review"]
        revisions = state.get("revision_count", 0)

        pass_quality_gate = (
            review.approved
            and review.quality_score >= self.settings.review_pass_score
            and not review.unsupported_claims
        )

        if pass_quality_gate:
            return "finish"

        if revisions < self.settings.max_review_revisions:
            return "revise"

        return "finish"

    async def generate(
        self,
        request: ResumeGenerateRequest,
        request_id: str,
    ) -> ResumeGenerateResponse:
        logger.info("workflow_started", extra={"event": "workflow_started"})
        final_state = await self.graph.ainvoke({"profile": request})

        review = final_state["review"]
        passed = (
            review.approved
            and review.quality_score >= self.settings.review_pass_score
            and not review.unsupported_claims
        )

        response = ResumeGenerateResponse(
            request_id=request_id,
            status="completed" if passed else "completed_with_warnings",
            profile_analysis=final_state["profile_analysis"],
            ats_optimization=final_state["ats_optimization"],
            resume=final_state["resume"],
            review=review,
            revision_count=final_state.get("revision_count", 0),
        )

        logger.info(
            "workflow_completed",
            extra={"event": "workflow_completed"},
        )
        return response
