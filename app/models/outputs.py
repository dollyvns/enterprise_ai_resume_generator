from typing import Literal

from pydantic import BaseModel, Field


class ProfileAnalysis(BaseModel):
    candidate_level: Literal[
        "Entry-Level",
        "Junior",
        "Mid-Level",
        "Senior",
        "Lead",
        "Principal",
        "Architect",
        "Executive",
    ]
    primary_domain: str = Field(min_length=1, max_length=200)
    years_experience: float = Field(ge=0, le=60)
    top_skills: list[str] = Field(default_factory=list, max_length=20)
    strengths: list[str] = Field(default_factory=list, max_length=10)
    gaps: list[str] = Field(default_factory=list, max_length=10)


class ATSOptimization(BaseModel):
    matched_keywords: list[str] = Field(default_factory=list, max_length=40)
    missing_keywords: list[str] = Field(default_factory=list, max_length=40)
    recommended_keywords: list[str] = Field(default_factory=list, max_length=40)
    ats_score: int = Field(ge=0, le=100)
    skill_alignment: str = Field(min_length=1, max_length=1200)
    formatting_suggestions: list[str] = Field(default_factory=list, max_length=15)


class ExperienceSection(BaseModel):
    company: str
    role: str
    date_range: str | None = None
    bullets: list[str] = Field(min_length=1, max_length=12)


class ProjectSection(BaseModel):
    name: str
    description: str
    bullets: list[str] = Field(default_factory=list, max_length=8)


class ResumeContent(BaseModel):
    headline: str = Field(min_length=1, max_length=250)
    professional_summary: str = Field(min_length=1, max_length=2000)
    core_skills: list[str] = Field(min_length=1, max_length=50)
    experience: list[ExperienceSection] = Field(default_factory=list, max_length=30)
    projects: list[ProjectSection] = Field(default_factory=list, max_length=20)
    education: list[str] = Field(default_factory=list, max_length=20)
    certifications: list[str] = Field(default_factory=list, max_length=30)


class ReviewResult(BaseModel):
    approved: bool
    quality_score: int = Field(ge=0, le=100)
    grammar_issues: list[str] = Field(default_factory=list, max_length=20)
    consistency_issues: list[str] = Field(default_factory=list, max_length=20)
    professionalism_issues: list[str] = Field(default_factory=list, max_length=20)
    unsupported_claims: list[str] = Field(default_factory=list, max_length=20)
    revision_instructions: list[str] = Field(default_factory=list, max_length=20)


class ResumeGenerateResponse(BaseModel):
    request_id: str
    status: Literal["completed", "completed_with_warnings"]
    profile_analysis: ProfileAnalysis
    ats_optimization: ATSOptimization
    resume: ResumeContent
    review: ReviewResult
    revision_count: int
