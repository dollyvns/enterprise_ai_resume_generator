from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_orchestrator
from app.core.security import TokenPrincipal, require_scope
from app.models.outputs import ResumeGenerateResponse
from app.models.profile import ResumeGenerateRequest
from app.orchestration.graph import ResumeOrchestrator

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])


@router.post(
    "/generate",
    response_model=ResumeGenerateResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_resume(
    payload: ResumeGenerateRequest,
    request: Request,
    _principal: Annotated[
        TokenPrincipal,
        Depends(require_scope("resume:generate")),
    ],
    orchestrator: Annotated[ResumeOrchestrator, Depends(get_orchestrator)],
) -> ResumeGenerateResponse:
    # Never log payload/profile data here; it may contain PII.
    return await orchestrator.generate(
        request=payload,
        request_id=request.state.request_id,
    )
