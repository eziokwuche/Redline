from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DeltaComparison, GradingResult, Resume
from app.schemas import CompareRequest, DeltaResponse, GradingLLMResponse
from app.services.grading import compare_versions
from app.services.llm_client import LLMGenerationError, get_llm_provider

router = APIRouter()


@router.post('/compare', response_model=DeltaResponse)
async def compare_resumes(
    payload: CompareRequest,
    db: Session = Depends(get_db),
):
    if payload.previous_grading_id == payload.current_grading_id:
        raise HTTPException(status_code=400, detail='Choose two distinct grading results to compare.')

    previous = db.query(GradingResult).filter(GradingResult.id == payload.previous_grading_id).first()
    current = db.query(GradingResult).filter(GradingResult.id == payload.current_grading_id).first()
    if previous is None or current is None:
        raise HTTPException(status_code=404, detail='One or both grading records were not found.')
    if previous.resume_id != current.resume_id or previous.job_description_id != current.job_description_id:
        raise HTTPException(status_code=400, detail='The grading results must belong to the same resume and job description.')

    resume = db.query(Resume).filter(Resume.id == previous.resume_id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail='Resume for grading results not found.')

    previous_payload = previous.raw_response.get('grading', previous.raw_response)
    current_payload = current.raw_response.get('grading', current.raw_response)
    previous_grading = GradingLLMResponse.model_validate(previous_payload)
    current_grading = GradingLLMResponse.model_validate(current_payload)
    previous_resume_text = previous.raw_response.get('resume_text', resume.raw_text)
    current_resume_text = current.raw_response.get('resume_text', resume.raw_text)
    try:
        provider = get_llm_provider()
        delta = compare_versions(
            provider,
            previous_resume_text,
            previous_grading,
            current_resume_text,
            current_grading,
        )
    except (LLMGenerationError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    comparison = DeltaComparison(
        previous_grading_id=previous.id,
        current_grading_id=current.id,
        score_delta=delta.score_delta,
        category_deltas=[item.model_dump(mode='json') for item in delta.category_deltas],
        resolved_issues=delta.resolved_issues,
        new_issues=delta.new_issues,
        verdict=delta.verdict,
    )
    db.add(comparison)
    db.commit()
    db.refresh(comparison)

    return DeltaResponse(
        id=comparison.id,
        previous_grading_id=previous.id,
        current_grading_id=current.id,
        score_delta=delta.score_delta,
        category_deltas=delta.category_deltas,
        resolved_issues=delta.resolved_issues,
        new_issues=delta.new_issues,
        verdict=delta.verdict,
    )
