# Redline — Resume ATS

Redline is a local AI-assisted resume review tool. Upload a PDF or DOCX resume, paste a target job description, receive an ATS-style score, then create and approve a tailored resume draft before downloading it as a polished PDF.

FastAPI + SQLite power the backend; React + Vite power the frontend. LLM extraction, grading, and draft generation support Groq, Gemini, or Ollama.

## What works today

- PDF/DOCX upload and text extraction, including DOCX table cells.
- Structured `ResumeProfile` extraction stored with each resume.
- Graceful profile-extraction failure: raw text remains usable and the upload reports `extraction_status: "failed"`.
- Session-scoped job descriptions.
- Initial raw-text grading and persisted grading history.
- AI-generated, user-reviewable resume drafts that can be edited, approved, rescanned, and saved as profile revisions.
- Regrading an edited `ResumeProfile` through `/rescan`.
- Comparison of two grading results for the same resume/job pair.
- Server-side PDF compilation from the stored profile via Jinja2 and `pdflatex`.
- Upload → job description → diagnosis → AI draft review → approved PDF-download frontend flow, including visible loading feedback.

## How tailored drafts work

1. Upload a resume and paste the target job description.
2. Redline extracts a structured profile and grades the original resume against that role.
3. Select **Create tailored draft** to generate a proposed rewrite using the stored profile, job description, and latest grading feedback.
4. Review every field, edit anything that needs correction, or restore an entire section to the original version.
5. Select **Approve, rescan, and save version**. Only this user-submitted profile is saved as a new revision and regraded.
6. Download the approved profile as an ATS-friendly PDF.

The AI draft is deliberately not applied automatically. The prompt instructs the model not to invent employers, roles, dates, degrees, skills, metrics, achievements, or contact information. Users should still verify all wording before approving a version.

## Current limitations

- The frontend supports drafting, reviewing, approving, rescanning, and downloading a PDF. Grade comparison is currently API-only.
- Drafting requires a successful structured-profile extraction. If an upload reports `extraction_status: "failed"`, its raw text can still be graded but there is no profile available to draft or compile.
- SQLite is the local database. Database migrations and PostgreSQL support are intentionally deferred until the schema stabilizes.
- PDF compilation requires a local LaTeX installation, such as MiKTeX, with `pdflatex` available to the backend process.
- PDF export uses Redline's consistent LaTeX template; it does not preserve the visual design of the uploaded file.
- Authentication and multi-user SaaS features are out of scope.

## Requirements

- Windows PowerShell
- Python with a virtual environment
- Node.js and npm
- MiKTeX / `pdflatex` for PDF compilation
- One configured LLM provider: Groq, Gemini, or Ollama

## Configure the backend

Create a root `.env` file. Never commit it.

```dotenv
DATABASE_URL=sqlite:///./ats.db
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-3.6-flash
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
MAX_UPLOAD_MB=10
UPLOAD_DIR=storage/uploads
ENVIRONMENT=development
```

Set `LLM_PROVIDER` to `gemini`, `groq`, or `ollama`. Only the selected provider needs usable credentials.

## Run locally

Install dependencies once:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm install
cd ..
```

Start the backend from the repository root:

```powershell
.\start-backend.ps1
```

The script clears port 8000, verifies it is free, then starts Uvicorn with reload enabled.

In a second terminal, start the frontend:

```powershell
.\start-frontend.ps1
```

Use the Redline application at [http://127.0.0.1:5173](http://127.0.0.1:5173). Explore the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API lifecycle

1. `POST /api/resumes` uploads a PDF/DOCX, extracts text, and attempts profile extraction.
2. `POST /api/job-descriptions` saves a session-scoped job description.
3. `POST /api/grade` performs the initial raw-text grade and persists a `GradingResult`.
4. `POST /api/resumes/{resume_id}/draft` proposes a tailored profile without saving it.
5. `POST /api/resumes/{resume_id}/rescan` saves a user-approved profile revision, grades formatted profile text, and persists another result.
6. `POST /api/compare` compares two distinct grading IDs for the same resume and job description.
7. `POST /api/resumes/{resume_id}/compile` returns a generated PDF for a resume with `profile_json`.

`/grade` establishes the initial baseline. `/draft` never saves model output. `/rescan` only saves the profile submitted by the user; if it is the first grade for a resume/job pair, it creates that pair’s baseline.

## Development checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run build
```

## Project layout

```text
app/                 FastAPI application, services, templates, and routers
frontend/            React/Vite client
tests/               Backend pytest suite
storage/uploads/     Local uploaded files (Git-ignored)
start-backend.ps1    Cleans port 8000 and starts the API
start-frontend.ps1   Cleans port 5173 and starts Vite
```

## Security

- Keep API keys only in `.env`.
- Never paste credentials into shell commands, source files, test data, or Git history.
- Rotate any exposed key immediately.
- `.env`, `ats.db`, uploads, generated PDFs, and logs are Git-ignored.
