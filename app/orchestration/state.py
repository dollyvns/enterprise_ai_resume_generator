from typing import TypedDict

from app.models.outputs import ATSOptimization, ProfileAnalysis, ResumeContent, ReviewResult
from app.models.profile import ResumeGenerateRequest


class ResumeState(TypedDict, total=False):
    profile: ResumeGenerateRequest
    profile_analysis: ProfileAnalysis
    ats_optimization: ATSOptimization
    resume: ResumeContent
    review: ReviewResult
    revision_count: int
