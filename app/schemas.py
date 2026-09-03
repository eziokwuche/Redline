from typing import Literal, Optional

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    technical_skills_match: int = Field(..., ge=0, le=100)
    experience_relevance: int = Field(..., ge=0, le=100)
    keyword_optimization: int = Field(..., ge=0, le=100)
    action_verb_strength: int = Field(..., ge=0, le=100)
    quantifiable_impact: int = Field(..., ge=0, le=100)


class Strength(BaseModel):
    category: str
    observation: str
    evidence: str


class Improvement(BaseModel):
    category: str
    issue: str
    suggestion: str
    example_rewrite: str


class GradingLLMResponse(BaseModel):
    overall_match_score: int = Field(..., ge=0, le=100)
    score_breakdown: ScoreBreakdown
    strengths: list[Strength] = Field(..., min_length=1, max_length=6)
    areas_for_improvement: list[Improvement] = Field(..., min_length=1, max_length=6)
    missing_keywords: list[str]
    ats_compatibility_flags: list[str]


class CategoryDelta(BaseModel):
    category: str
    previous: int = Field(..., ge=0, le=100)
    current: int = Field(..., ge=0, le=100)
    delta: int


class DeltaQualitativeResponse(BaseModel):
    resolved_issues: list[str]
    new_issues: list[str]
    verdict: str


class DeltaLLMResponse(BaseModel):
    score_delta: int
    category_deltas: list[CategoryDelta]
    resolved_issues: list[str]
    new_issues: list[str]
    verdict: str


class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)


class GradingRequest(BaseModel):
    resume_id: int
    job_description_id: int
    target_company: Optional[str] = None


class CompareRequest(BaseModel):
    previous_grading_id: int = Field(..., gt=0)
    current_grading_id: int = Field(..., gt=0)


class ResumeUploadResponse(BaseModel):
    id: int
    session_id: str
    version: int
    original_filename: str
    file_type: str
    extraction_method: str
    extraction_status: Literal['success', 'failed']
    extraction_error: str | None = None
    raw_text_preview: str = Field(..., max_length=2000)


class GradingResponse(BaseModel):
    id: int
    resume_id: int
    job_description_id: int
    overall_score: int
    score_breakdown: ScoreBreakdown
    strengths: list[Strength]
    improvements: list[Improvement]
    missing_keywords: list[str]
    ats_flags: list[str]
    llm_provider: str
    llm_model: str


class DeltaResponse(BaseModel):
    id: int
    previous_grading_id: int
    current_grading_id: int
    score_delta: int
    category_deltas: list[CategoryDelta]
    resolved_issues: list[str]
    new_issues: list[str]
    verdict: str


class EducationEntry(BaseModel):
    institution: str
    location: str
    degree: str
    dates: str


class ExperienceEntry(BaseModel):
    title: str
    dates: str
    organization: str
    location: str
    bullets: list[str]


class ProjectEntry(BaseModel):
    name: str
    tech_stack: str
    dates: str
    bullets: list[str]


class SkillCategory(BaseModel):
    category: str
    items: list[str]


class ResumeProfile(BaseModel):
    name: str
    phone: str
    email: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    education: list[EducationEntry]
    experience: list[ExperienceEntry]
    projects: list[ProjectEntry]
    skills: list[SkillCategory]


class RescanRequest(BaseModel):
    profile: ResumeProfile
    job_description_id: int
    target_company: Optional[str] = None
