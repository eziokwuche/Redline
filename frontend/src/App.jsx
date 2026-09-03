import { useState } from 'react'
import ResumeUpload from './components/ResumeUpload.jsx'
import JobDescriptionForm from './components/JobDescriptionForm.jsx'
import GradingReport from './components/GradingReport.jsx'
import DeltaReport from './components/DeltaReport.jsx'
import { uploadResume, createJobDescription, gradeResume, compareVersions } from './api.js'

const initialState = {
  step: 'upload', // upload | job | report | revise | delta
  sessionId: null,
  job: null,
  pendingResume: null,
  gradings: [], // [{ resumeId, version, gradingId, result }]
  deltaResult: null,
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

  const handleReviseUpload = async (file) => {
    setLoading(true)
    setError(null)
    // Capture the previous grading before any state updates below — this is
    // the "before" side of the comparison, and must not shift under us.
    const previous = state.gradings[state.gradings.length - 1]
    try {
      const uploadRes = await uploadResume(file, state.sessionId)
      const gradingRes = await gradeResume(uploadRes.id, state.job.id)
      const entry = {
        resumeId: uploadRes.id,
        version: uploadRes.version,
        gradingId: gradingRes.id,
        result: gradingRes,
      }
      const deltaRes = await compareVersions(previous.gradingId, gradingRes.id)
      patch({
        gradings: [...state.gradings, entry],
        deltaResult: deltaRes,
        step: 'delta',
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const latestGrading = state.gradings[state.gradings.length - 1]

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
            onRevise={() => patch({ step: 'revise' })}
            onSkipRevise={restart}
          />
        )}

        {state.step === 'revise' && (
          <ResumeUpload
            title="Revised resume"
            subtitle={`A new version, still targeting "${state.job?.title}".`}
            onUpload={handleReviseUpload}
            loading={loading}
            error={error}
          />
        )}

        {state.step === 'delta' && state.deltaResult && (
          <DeltaReport result={state.deltaResult} onRestart={restart} />
        )}
      </main>

      <footer className="app-footer">
        <span>session {state.sessionId ? state.sessionId.slice(0, 8) : '—'}</span>
      </footer>
    </div>
  )
}
