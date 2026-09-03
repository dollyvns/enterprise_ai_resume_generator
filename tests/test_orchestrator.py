from pydantic import BaseModel

from app.core.config import Settings
from app.models.outputs import (
    ATSOptimization,
    ProfileAnalysis,
    ResumeContent,
    ReviewResult,
)
from app.models.profile import ResumeGenerateRequest
from app.orchestration.graph import ResumeOrchestrator
import pytest


class FakeLLM:
    def __init__(self):
        self.review_calls = 0

    async def generate(self, schema: type[BaseModel], system_prompt: str, payload: dict):
        if schema is ProfileAnalysis:
            return ProfileAnalysis(
                candidate_level="Senior",
                primary_domain="Software Engineering",
                years_experience=10,
                top_skills=["Python", "FastAPI"],
                strengths=["API design"],
                gaps=[],
            )
        if schema is ATSOptimization:
            return ATSOptimization(
                matched_keywords=["Python", "FastAPI"],
                missing_keywords=[],
                recommended_keywords=["REST APIs"],
                ats_score=88,
                skill_alignment="Strong alignment.",
                formatting_suggestions=["Use standard section headings."],
            )
        if schema is ResumeContent:
            return ResumeContent(
                headline="Senior Software Engineer",
                professional_summary="Senior engineer focused on reliable API platforms.",
                core_skills=["Python", "FastAPI"],
                experience=[
                    {
                        "company": "Example Corp",
                        "role": "Senior Engineer",
                        "date_range": "2020-Present",
                        "bullets": ["Built reliable API services using Python and FastAPI."],
                    }
                ],
                projects=[],
                education=[],
                certifications=[],
            )
        if schema is ReviewResult:
            self.review_calls += 1
            # Force exactly one revision on first review.
            if self.review_calls == 1:
                return ReviewResult(
                    approved=False,
                    quality_score=80,
                    grammar_issues=[],
                    consistency_issues=[],
                    professionalism_issues=["Summary can be more targeted."],
                    unsupported_claims=[],
                    revision_instructions=["Make the summary more specific to the target role."],
                )
            return ReviewResult(
                approved=True,
                quality_score=92,
                grammar_issues=[],
                consistency_issues=[],
                professionalism_issues=[],
                unsupported_claims=[],
                revision_instructions=[],
            )
        raise AssertionError(f"Unexpected schema: {schema}")


async def test_orchestrator_reviewer_loop():
    settings = Settings(
        jwt_secret="a-very-long-unit-test-secret-over-32-characters",
        app_user_password_hash="not-used",
        openai_api_key="test",
        openai_model="test-model",
        max_review_revisions=1,
        review_pass_score=85,
    )
    orchestrator = ResumeOrchestrator(FakeLLM(), settings)

    request = ResumeGenerateRequest(
        target_role="Senior Software Engineer",
        skills=["Python", "FastAPI"],
        experience=[
            {
                "company": "Example Corp",
                "role": "Senior Engineer",
                "current": True,
                "responsibilities": ["Build APIs"],
                "technologies": ["Python", "FastAPI"],
            }
        ],
    )

    response = await orchestrator.generate(request, request_id="test-request-id")

    assert response.status == "completed"
    assert response.revision_count == 1
    assert response.review.quality_score == 92


@pytest.mark.asyncio
async def test_orchestrator_reviewer_loop():
    result = await some_async_function()

    assert result is not None