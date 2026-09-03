# Resume ATS

A FastAPI-based application to parse resumes, score them against job descriptions, and compare multiple candidates or resume versions.

## Features

- Upload resume PDFs and DOCX files
- Extract text content from uploaded documents
- Compare resume content against job requirements
- Generate a grading summary with strengths, gaps, and recommendations
- Persist metadata in PostgreSQL via SQLAlchemy
- Optional Alembic migrations for schema evolution

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- PDF/DOCX text extraction
- LLM abstraction for Groq, Gemini, or Ollama

## Local development

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
4. Start PostgreSQL locally:
   ```bash
   docker compose up -d postgres
   ```
5. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```

If you encounter a PostgreSQL driver install issue on Windows, this repo uses the binary-friendly `psycopg` driver and expects the connection string to use `postgresql+psycopg://...`.

The app is available at http://localhost:8000.

## API endpoints

- POST /api/resumes
- POST /api/job-descriptions
- POST /api/grade
- POST /api/compare

## Testing

```bash
pytest -q
```

## Notes

- Do not commit your `.env` file.
- Uploaded resume files are stored under `storage/uploads` and are ignored by Git.
