# Redline — resume review frontend

A React (Vite) frontend for the Resume ATS backend. Upload a resume, paste a
job description, get a structured diagnosis, then upload a revision to see
whether it actually got stronger.

## One required backend change first

The FastAPI backend's CORS config only allows `http://localhost:3000` by
default. Vite runs on **5173**. Open `app/main.py` in the backend repo and
add the Vite origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Without this, every request from the frontend will fail with a CORS error
in the browser console — it's not a bug in the frontend code, the backend
is just refusing to talk to a port it doesn't recognize yet.

## Setup

```bash
npm install
cp .env.example .env   # only edit this if your backend runs somewhere other than :8000
npm run dev
```

Open the URL it prints (`http://localhost:5173`). Make sure the backend
(`uvicorn app.main:app --reload`) is running at the same time in a separate
terminal — this app has no functionality without it.

## What it does

1. **Upload a resume** (PDF/DOCX) — drag-and-drop or click to browse.
2. **Paste a job description** — title, optional company, full posting text.
3. **Get the diagnosis** — overall score, a five-category breakdown, what's
   working (with the exact resume line it's based on), and concrete
   "redline" notes with a suggested rewrite for each issue.
4. **Optionally upload a revised resume** — it's graded fresh, then diffed
   against the previous version: what improved, what's still broken, what's
   newly broken, and a plain-language verdict on whether it's actually
   stronger.

## Structure

```
src/
  App.jsx                    State machine: upload → job → report → revise → delta
  api.js                     fetch wrappers for every backend endpoint
  styles.css                 Design tokens + all component styles
  components/
    ResumeUpload.jsx           Drag-and-drop file upload
    JobDescriptionForm.jsx      Job posting intake form
    GradingReport.jsx            Score gauges + strength/issue annotations
    DeltaReport.jsx               Before/after comparison view
```

No routing library, no state management library — the whole flow is one
`useState` state machine in `App.jsx`. That's a deliberate choice at this
size: four linear steps don't need React Router or Redux, and adding either
would be complexity with nothing to show for it. If you extend this to
multiple concurrent sessions or a resume history page, that's the point
where reaching for a router starts paying for itself.
