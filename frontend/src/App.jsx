import { useState } from 'react'
import ResumeUpload from './components/ResumeUpload.jsx'
import JobDescriptionForm from './components/JobDescriptionForm.jsx'
import GradingReport from './components/GradingReport.jsx'
import ResumeEditor from './components/ResumeEditor.jsx'
import { uploadResume, createJobDescription, createResumeDraft, compileResume, gradeResume, rescanResume } from './api.js'

const initialState = {
  step: 'upload', // upload | job | report | editor
  sessionId: null,
  job: null,
  pendingResume: null,
  gradings: [], // [{ resumeId, version, gradingId, result }]
}

export default function App() {
  const [state, setState] = useState(initialState)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const patch = (partial) => setState((s) => ({ ...s, ...partial }))

  const restart = () => {
    setState(initialState)
    setError(null)
  }

  const handleFirstUpload = async (file) => {
    setLoading(true)
    setError(null)
    try {
      const res = await uploadResume(file, state.sessionId)
      patch({ sessionId: res.session_id, pendingResume: res, step: 'job' })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleJobSubmit = async (payload) => {
    setLoading(true)
    setError(null)
    try {
      const jobRes = await createJobDescription(payload, state.sessionId)
      const gradingRes = await gradeResume(state.pendingResume.id, jobRes.job_description_id)
      const entry = {
        resumeId: state.pendingResume.id,
        version: state.pendingResume.version,
        gradingId: gradingRes.id,
        result: gradingRes,
      }
      patch({
        job: { id: jobRes.job_description_id, title: payload.title },
        gradings: [entry],
        pendingResume: null,
        step: 'report',
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateDraft = async () => {
    setLoading(true)
    setError(null)
    try {
      const draft = await createResumeDraft(latestGrading.resumeId, state.job.id)
      patch({ draft, step: 'editor' })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleApplyDraft = async (profile) => {
    setLoading(true)
    setError(null)
    try {
      const gradingRes = await rescanResume(latestGrading.resumeId, profile, state.job.id)
      patch({
        gradings: [...state.gradings, {
          resumeId: latestGrading.resumeId,
          version: latestGrading.version,
          gradingId: gradingRes.id,
          result: gradingRes,
        }],
        draft: null,
        step: 'report',
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPdf = async () => {
    setLoading(true)
    setError(null)
    try {
      const pdf = await compileResume(latestGrading.resumeId)
      const url = URL.createObjectURL(pdf)
      const link = document.createElement('a')
      link.href = url
      link.download = 'redline-resume.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const latestGrading = state.gradings[state.gradings.length - 1]
  const loadingCopy = state.step === 'upload'
    ? ['Reading your resume', 'Extracting text and building your profile…']
    : state.step === 'editor'
      ? ['Saving your approved changes', 'Creating a new version and rescanning it…']
    : ['Scoring your resume', 'Comparing skills, experience, and keywords…']

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="wordmark">Redline</span>
        <span className="wordmark-sub">mark up your resume before an ATS does</span>
      </header>

      <main className="app-main">
        {state.step === 'upload' && (
          <ResumeUpload
            title="Your resume"
            subtitle="PDF or DOCX. It's parsed for text, nothing more."
            onUpload={handleFirstUpload}
            loading={loading}
            error={error}
          />
        )}

        {state.step === 'job' && (
          <JobDescriptionForm onSubmit={handleJobSubmit} loading={loading} error={error} />
        )}

        {state.step === 'report' && latestGrading && (
          <GradingReport
            result={latestGrading.result}
            onCreateDraft={handleCreateDraft}
            onDownloadPdf={state.gradings.length > 1 ? handleDownloadPdf : null}
            onRestart={restart}
            error={error}
          />
        )}

        {state.step === 'editor' && state.draft && (
          <ResumeEditor
            draft={state.draft}
            onApply={handleApplyDraft}
            onBack={() => { setError(null); patch({ step: 'report' }) }}
            loading={loading}
            error={error}
          />
        )}
      </main>
      {loading && <div className="loading-layer" role="status" aria-live="polite"><div className="loading-card"><span className="loading-orb" /><p>REDLINE IS WORKING</p><h2>{loadingCopy[0]}</h2><span>{loadingCopy[1]}</span><div className="buffer-track"><i /></div></div></div>}

      <footer className="app-footer">
        <span>session {state.sessionId ? state.sessionId.slice(0, 8) : '—'}</span>
      </footer>
    </div>
  )
}
