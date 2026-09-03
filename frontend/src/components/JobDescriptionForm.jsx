import { useState } from 'react'

export default function JobDescriptionForm({ onSubmit, loading, error }) {
  const [title, setTitle] = useState('')
  const [rawText, setRawText] = useState('')

  const tooShort = rawText.trim().length > 0 && rawText.trim().length < 50

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ title, description: rawText })
  }

  return (
    <section className="panel">
      <h2 className="panel-title">Target role</h2>
      <p className="panel-subtitle">Paste the job posting you're aiming for.</p>

      <form onSubmit={handleSubmit} className="form">
        <label className="field">
          <span className="field-label">Role title</span>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Senior Backend Engineer"
          />
        </label>

        <label className="field">
          <span className="field-label">Full job description</span>
          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            required
            rows={10}
            placeholder="Paste the full posting — requirements, responsibilities, everything."
          />
        </label>

        {tooShort && <p className="field-hint">A few more lines will give a much sharper read.</p>}
        {error && <p className="field-error">{error}</p>}

        <button type="submit" className="btn-primary" disabled={loading || rawText.trim().length < 50}>
          {loading ? 'Grading…' : 'Continue to diagnosis'}
        </button>
      </form>
    </section>
  )
}
