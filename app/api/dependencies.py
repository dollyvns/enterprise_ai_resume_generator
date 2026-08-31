from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.orchestration.graph import ResumeOrchestrator
from app.services.llm import OpenAIStructuredLLM


@lru_cache
def _build_orchestrator() -> ResumeOrchestrator:
    settings = get_settings()
    llm = OpenAIStructuredLLM(settings)
    return ResumeOrchestrator(llm, settings)


def get_orchestrator(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ResumeOrchestrator:
    # settings dependency is intentional so FastAPI documents/injects application config.
    _ = settings
    return _build_orchestrator()
