import shutil
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session

import logging

from app.config import settings
from app.database import get_db
from app.models import JobDescription, Resume, UserSession
from app.schemas import JobDescriptionCreate, ResumeUploadResponse
from app.services.grading import extract_profile
from app.services.latex_renderer import render_resume_template

# Provider-specific exception imports (optional)
try:
    import google.genai.errors as google_errors
except ImportError:
    google_errors = None

try:
    from groq import GroqError
except ImportError:
    GroqError = None

from app.services.llm_client import LLMGenerationError, get_llm_provider
from app.services.text_extraction import extract_resume_text

logger = logging.getLogger(__name__)
router = APIRouter()


def get_or_create_session(db: Session, session_id: str | None) -> str:
    if session_id:
        existing = db.query(UserSession).filter(UserSession.id == session_id).first()
        if existing:
            return existing.id

    new_session_id = session_id or str(uuid4())
    db.add(UserSession(id=new_session_id))
    db.commit()
    return new_session_id


@router.post('/resumes', response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    session_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if file.filename is None:
        raise HTTPException(status_code=400, detail='No file selected.')

    suffix = Path(file.filename).suffix.lower()
    if suffix not in {'.pdf', '.docx'}:
        raise HTTPException(status_code=400, detail='Unsupported file type.')

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='Uploaded file is empty.')

    max_size = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail='File exceeds the allowed size.')

    final_session_id = get_or_create_session(db, session_id)
    storage_path = Path(settings.upload_dir) / f"{uuid4()}{suffix}"
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_bytes(content)

    try:
        extraction = extract_resume_text(storage_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Build exception tuple dynamically to include provider-specific exceptions
    base_exceptions = (LLMGenerationError, RuntimeError, ValueError)
    provider_exceptions = []
    if google_errors:
        provider_exceptions.append(google_errors.ClientError)
    if GroqError:
        provider_exceptions.append(GroqError)
    catchable_exceptions = tuple(base_exceptions + tuple(provider_exceptions))

    profile_payload = None
    extraction_status = 'success'
    extraction_error = None
    try:
        provider = get_llm_provider()
        profile = extract_profile(provider, extraction.text)
        profile_payload = profile.model_dump(mode='json')
    except catchable_exceptions as exc:
        logger.warning('Resume profile extraction failed during upload; leaving profile_json as null.', exc_info=True)
        profile_payload = None
        extraction_status = 'failed'
        extraction_error = str(exc)

    next_version = (db.query(func.coalesce(func.max(Resume.version), 0)).filter(Resume.session_id == final_session_id).scalar() or 0) + 1

    resume = Resume(
        session_id=final_session_id,
        version=next_version,
        original_filename=file.filename,
        file_type=suffix.lstrip('.'),
        raw_text=extraction.text,
        extraction_method=extraction.method,
        profile_json=profile_payload,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(
        id=resume.id,
        session_id=resume.session_id,
        version=resume.version,
        original_filename=resume.original_filename,
        file_type=resume.file_type,
        extraction_method=resume.extraction_method,
        extraction_status=extraction_status,
        extraction_error=extraction_error,
        raw_text_preview=extraction.text[:2000],
    )


@router.post('/resumes/{resume_id}/compile')
async def compile_resume(
    resume_id: int,
    timeout: float = Query(default=10.0, ge=0.1, le=120.0),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail='Resume not found.')
    if not resume.profile_json:
        raise HTTPException(status_code=404, detail='Resume has no stored profile_json for compilation.')

    temp_dir = Path(tempfile.mkdtemp(prefix='resume_compile_'))
    tex_path = temp_dir / 'resume.tex'
    pdf_path = temp_dir / 'resume.pdf'

    def cleanup_dir() -> None:
        shutil.rmtree(temp_dir, ignore_errors=True)

    try:
        tex_path.write_text(render_resume_template(resume.profile_json), encoding='utf-8')
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'resume.tex'],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if not pdf_path.exists():
            diagnostics = f'stdout:\n{result.stdout}\nstderr:\n{result.stderr}'
            logger.error('pdflatex completed without producing a PDF.\n%s', diagnostics)
            detail = 'pdflatex completed without producing a PDF.'
            if settings.environment == 'development':
                detail = f'{detail}\n\nCompiler diagnostics:\n{diagnostics}'
            raise HTTPException(status_code=500, detail=detail)
    except subprocess.TimeoutExpired as exc:
        cleanup_dir()
        raise HTTPException(status_code=504, detail=f'pdflatex timed out after {exc.timeout} seconds.') from exc
    except HTTPException:
        cleanup_dir()
        raise
    except Exception as exc:
        cleanup_dir()
        raise HTTPException(status_code=500, detail=f'Failed to compile resume: {exc}') from exc

    return FileResponse(
        path=pdf_path,
        filename=f'{Path(resume.original_filename).stem}.pdf',
        background=BackgroundTask(cleanup_dir),
    )


@router.post('/job-descriptions', response_model=dict)
async def create_job_description(
    payload: JobDescriptionCreate,
    session_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    final_session_id = get_or_create_session(db, session_id)
    jd = JobDescription(
        session_id=final_session_id,
        title=payload.title,
        raw_text=payload.description,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return {
        'job_description_id': jd.id,
        'session_id': jd.session_id,
    }
