from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GradingResult, JobDescription, Resume
from app.schemas import GradingLLMResponse, GradingRequest, GradingResponse, RescanRequest
from app.services.grading import grade_resume, profile_to_text
from app.services.llm_client import LLMGenerationError, get_llm_provider

router = APIRouter()


# Initial grading: grade the uploaded resume's raw extracted text and persist the result.
# Comparison lookup is deferred to /compare (Part 1.6); "prior grading" means the most
# recent GradingResult by created_at for this (resume_id, job_description_id) pair,
# regardless of whether /grade or /rescan created it.
@router.post('/grade', response_model=GradingResponse)
async def grade_resume_endpoint(
    payload: GradingRequest,
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
    job = db.query(JobDescription).filter(JobDescription.id == payload.job_description_id).first()
    if resume is None or job is None:
        raise HTTPException(status_code=404, detail='Resume or job description not found.')

    try:
        provider = get_llm_provider()
        result = grade_resume(provider, resume.raw_text, job.raw_text, payload.target_company)
    except LLMGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    grading = GradingResult(
        resume_id=resume.id,
        job_description_id=job.id,
        overall_score=result.overall_match_score,
        score_breakdown=result.score_breakdown.model_dump(mode='json'),
        strengths=[item.model_dump(mode='json') for item in result.strengths],
        improvements=[item.model_dump(mode='json') for item in result.areas_for_improvement],
        missing_keywords=result.missing_keywords,
        ats_flags=result.ats_compatibility_flags,
        llm_provider=provider.name,
        llm_model=getattr(provider, 'model', 'unknown'),
        raw_response={
            'grading': result.model_dump(mode='json'),
            'resume_text': resume.raw_text,
        },
    )
    db.add(grading)
    db.commit()
    db.refresh(grading)

    return GradingResponse(
        id=grading.id,
        resume_id=resume.id,
        job_description_id=job.id,
        overall_score=grading.overall_score,
        score_breakdown=result.score_breakdown,
        strengths=result.strengths,
        improvements=result.areas_for_improvement,
        missing_keywords=result.missing_keywords,
        ats_flags=result.ats_compatibility_flags,
        llm_provider=grading.llm_provider,
        llm_model=grading.llm_model,
    )


# Post-edit grading: persist the submitted ResumeProfile, grade its formatted text, and
# persist the result. Comparison lookup is deferred to /compare (Part 1.6); "prior
# grading" means the most recent GradingResult by created_at for this
# (resume_id, job_description_id) pair, regardless of which route created it. If no
# such result exists, /rescan proceeds and saves this result as that pair's baseline.
@router.post('/resumes/{resume_id}/rescan', response_model=GradingResponse)
async def rescan_resume_with_profile(
    resume_id: int,
    request: RescanRequest,
    db: Session = Depends(get_db),
):
    """
    Re-grade a resume using an edited ResumeProfile instead of raw text.
    
    Updates the stored profile_json and runs grading against the formatted profile text.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail='Resume not found.')
    
    job = db.query(JobDescription).filter(JobDescription.id == request.job_description_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail='Job description not found.')
    
    # Update the stored profile_json
    resume.profile_json = request.profile.model_dump(mode='json')
    db.add(resume)
    db.commit()
    
    # Convert the edited profile to text for grading
    edited_resume_text = profile_to_text(request.profile)
    
    # Run grading against the edited text
    try:
        provider = get_llm_provider()
        result = grade_resume(provider, edited_resume_text, job.raw_text, request.target_company)
    except LLMGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    
    # Create and save the grading result
    grading = GradingResult(
        resume_id=resume.id,
        job_description_id=job.id,
        overall_score=result.overall_match_score,
        score_breakdown=result.score_breakdown.model_dump(mode='json'),
        strengths=[item.model_dump(mode='json') for item in result.strengths],
        improvements=[item.model_dump(mode='json') for item in result.areas_for_improvement],
        missing_keywords=result.missing_keywords,
        ats_flags=result.ats_compatibility_flags,
        llm_provider=provider.name,
        llm_model=getattr(provider, 'model', 'unknown'),
        raw_response={
            'grading': result.model_dump(mode='json'),
            'resume_text': edited_resume_text,
        },
    )
    db.add(grading)
    db.commit()
    db.refresh(grading)
    
    return GradingResponse(
        id=grading.id,
        resume_id=resume.id,
        job_description_id=job.id,
        overall_score=grading.overall_score,
        score_breakdown=result.score_breakdown,
        strengths=result.strengths,
        improvements=result.areas_for_improvement,
        missing_keywords=result.missing_keywords,
        ats_flags=result.ats_compatibility_flags,
        llm_provider=grading.llm_provider,
        llm_model=grading.llm_model,
    )
