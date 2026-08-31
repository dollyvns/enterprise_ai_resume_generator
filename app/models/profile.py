from datetime import date
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

ShortText = Annotated[str, Field(min_length=1, max_length=300)]
LongText = Annotated[str, Field(min_length=1, max_length=6000)]


class ExperienceInput(BaseModel):
    company: ShortText
    role: ShortText
    start_date: date | None = None
    end_date: date | None = None
    current: bool = False
    location: str | None = Field(default=None, max_length=200)
    responsibilities: list[ShortText] = Field(default_factory=list, max_length=30)
    achievements: list[ShortText] = Field(default_factory=list, max_length=30)
    technologies: list[ShortText] = Field(default_factory=list, max_length=50)

    @field_validator("end_date")
    @classmethod
    def validate_date_order(cls, end_date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date must be after start_date")
        return end_date


class ProjectInput(BaseModel):
    name: ShortText
    description: LongText
    role: str | None = Field(default=None, max_length=300)
    technologies: list[ShortText] = Field(default_factory=list, max_length=50)
    outcomes: list[ShortText] = Field(default_factory=list, max_length=20)


class EducationInput(BaseModel):
    institution: ShortText
    degree: ShortText
    field_of_study: str | None = Field(default=None, max_length=300)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)


class CertificationInput(BaseModel):
    name: ShortText
    issuer: str | None = Field(default=None, max_length=300)
    year: int | None = Field(default=None, ge=1950, le=2100)


class ResumeGenerateRequest(BaseModel):
    # PII is optional because agents do not need it to analyze competency.
    name: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)

    target_role: ShortText
    target_job_description: str | None = Field(default=None, max_length=12000)

    skills: list[ShortText] = Field(min_length=1, max_length=100)
    experience: list[ExperienceInput] = Field(default_factory=list, max_length=30)
    projects: list[ProjectInput] = Field(default_factory=list, max_length=30)
    education: list[EducationInput] = Field(default_factory=list, max_length=20)
    certifications: list[CertificationInput] = Field(default_factory=list, max_length=30)
