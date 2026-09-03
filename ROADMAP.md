# Roadmap

## Phase 1: Foundation

- Set up project structure and environment config
- Add FastAPI app entrypoint and settings
- Configure PostgreSQL and Alembic
- Implement upload endpoint and file validation

## Phase 2: Resume processing

- Build document extraction for PDF and DOCX
- Normalize text and store resume metadata
- Add job description ingestion flow

## Phase 3: ATS grading

- Implement grading orchestration and scoring prompt templates
- Integrate LLM providers with a common interface
- Return structured feedback and fit score

## Phase 4: Comparison and polish

- Add compare endpoints and side-by-side analysis
- Add tests for uploads and grading workflow
- Hardening for validation, security, and performance

## Phase 5: Production-readiness

- Add CI, linting, and deployment config
- Improve observability and error handling
- Tune prompt quality and evaluation heuristics
