from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class JobDescription(Base):
    __tablename__ = 'job_descriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey('user_sessions.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Resume(Base):
    __tablename__ = 'resumes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey('user_sessions.id'), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GradingResult(Base):
    __tablename__ = 'grading_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id'), nullable=False, index=True)
    job_description_id: Mapped[int] = mapped_column(ForeignKey('job_descriptions.id'), nullable=False, index=True)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)
    strengths: Mapped[dict] = mapped_column(JSON, nullable=False)
    improvements: Mapped[dict] = mapped_column(JSON, nullable=False)
    missing_keywords: Mapped[dict] = mapped_column(JSON, nullable=False)
    ats_flags: Mapped[dict] = mapped_column(JSON, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_response: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ResumeRevision(Base):
    __tablename__ = 'resume_revisions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id'), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DeltaComparison(Base):
    __tablename__ = 'delta_comparisons'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    previous_grading_id: Mapped[int] = mapped_column(ForeignKey('grading_results.id'), nullable=False)
    current_grading_id: Mapped[int] = mapped_column(ForeignKey('grading_results.id'), nullable=False)
    score_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    category_deltas: Mapped[dict] = mapped_column(JSON, nullable=False)
    resolved_issues: Mapped[dict] = mapped_column(JSON, nullable=False)
    new_issues: Mapped[dict] = mapped_column(JSON, nullable=False)
    verdict: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
