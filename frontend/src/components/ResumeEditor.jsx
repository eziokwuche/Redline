import { useState } from 'react'

function SectionHeader({ title, onRestore }) {
  return (
    <div className="editor-section-header">
      <h3>{title}</h3>
      <button type="button" className="text-button" onClick={onRestore}>Restore original section</button>
    </div>
  )
}

function TextField({ label, value, onChange }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input value={value || ''} onChange={(event) => onChange(event.target.value)} />
    </label>
  )
}

export default function ResumeEditor({ draft, onApply, onBack, loading, error }) {
  const [profile, setProfile] = useState(() => structuredClone(draft.profile))
  const original = draft.current_profile

  const updateRoot = (key, value) => setProfile((current) => ({ ...current, [key]: value }))
  const restore = (key) => setProfile((current) => ({ ...current, [key]: structuredClone(original[key]) }))
  const updateEntry = (section, index, key, value) => setProfile((current) => ({
    ...current,
    [section]: current[section].map((entry, entryIndex) => entryIndex === index ? { ...entry, [key]: value } : entry),
  }))

  return (
    <section className="panel editor-panel">
      <p className="eyebrow">Review before saving</p>
      <h2 className="panel-title">Your tailored resume draft</h2>
      <p className="panel-subtitle">AI has suggested wording improvements. Verify every claim, then save only the version you approve.</p>

      <div className="draft-notes">
        <strong>Suggested focus</strong>
        <ul>{draft.changes_summary.map((note, index) => <li key={index}>{note}</li>)}</ul>
        {draft.factual_claims_to_verify.length > 0 && <>
          <strong>Confirm before using</strong>
          <ul>{draft.factual_claims_to_verify.map((note, index) => <li key={index}>{note}</li>)}</ul>
        </>}
      </div>

      <form className="editor-form" onSubmit={(event) => { event.preventDefault(); onApply(profile) }}>
        <div className="editor-section">
          <SectionHeader title="Contact" onRestore={() => ['name', 'phone', 'email', 'linkedin', 'github'].forEach((key) => updateRoot(key, original[key]))} />
          <div className="editor-grid">
            <TextField label="Name" value={profile.name} onChange={(value) => updateRoot('name', value)} />
            <TextField label="Phone" value={profile.phone} onChange={(value) => updateRoot('phone', value)} />
            <TextField label="Email" value={profile.email} onChange={(value) => updateRoot('email', value)} />
            <TextField label="LinkedIn" value={profile.linkedin} onChange={(value) => updateRoot('linkedin', value || null)} />
            <TextField label="GitHub" value={profile.github} onChange={(value) => updateRoot('github', value || null)} />
          </div>
        </div>

        <div className="editor-section">
          <SectionHeader title="Education" onRestore={() => restore('education')} />
          {profile.education.map((entry, index) => <div className="editor-entry" key={index}>
            <div className="editor-grid">
              <TextField label="Institution" value={entry.institution} onChange={(value) => updateEntry('education', index, 'institution', value)} />
              <TextField label="Degree" value={entry.degree} onChange={(value) => updateEntry('education', index, 'degree', value)} />
              <TextField label="Location" value={entry.location} onChange={(value) => updateEntry('education', index, 'location', value)} />
              <TextField label="Dates" value={entry.dates} onChange={(value) => updateEntry('education', index, 'dates', value)} />
            </div>
          </div>)}
          {profile.education.length === 0 && <p className="empty-note">No education entries in this resume.</p>}
        </div>

        <div className="editor-section">
          <SectionHeader title="Experience" onRestore={() => restore('experience')} />
          {profile.experience.map((entry, index) => <div className="editor-entry" key={index}>
            <div className="editor-grid">
              <TextField label="Role" value={entry.title} onChange={(value) => updateEntry('experience', index, 'title', value)} />
              <TextField label="Organization" value={entry.organization} onChange={(value) => updateEntry('experience', index, 'organization', value)} />
              <TextField label="Location" value={entry.location} onChange={(value) => updateEntry('experience', index, 'location', value)} />
              <TextField label="Dates" value={entry.dates} onChange={(value) => updateEntry('experience', index, 'dates', value)} />
            </div>
            <label className="field"><span className="field-label">Accomplishments — one bullet per line</span>
              <textarea rows={Math.max(4, entry.bullets.length + 1)} value={entry.bullets.join('\n')} onChange={(event) => updateEntry('experience', index, 'bullets', event.target.value.split('\n').map((line) => line.trim()).filter(Boolean))} />
            </label>
          </div>)}
          {profile.experience.length === 0 && <p className="empty-note">No experience entries in this resume.</p>}
        </div>

        <div className="editor-section">
          <SectionHeader title="Projects" onRestore={() => restore('projects')} />
          {profile.projects.map((entry, index) => <div className="editor-entry" key={index}>
            <div className="editor-grid">
              <TextField label="Project" value={entry.name} onChange={(value) => updateEntry('projects', index, 'name', value)} />
              <TextField label="Technology" value={entry.tech_stack} onChange={(value) => updateEntry('projects', index, 'tech_stack', value)} />
              <TextField label="Dates" value={entry.dates} onChange={(value) => updateEntry('projects', index, 'dates', value)} />
            </div>
            <label className="field"><span className="field-label">Project details — one bullet per line</span>
              <textarea rows={Math.max(4, entry.bullets.length + 1)} value={entry.bullets.join('\n')} onChange={(event) => updateEntry('projects', index, 'bullets', event.target.value.split('\n').map((line) => line.trim()).filter(Boolean))} />
            </label>
          </div>)}
          {profile.projects.length === 0 && <p className="empty-note">No projects in this resume.</p>}
        </div>

        <div className="editor-section">
          <SectionHeader title="Skills" onRestore={() => restore('skills')} />
          {profile.skills.map((entry, index) => <div className="editor-grid editor-entry" key={index}>
            <TextField label="Category" value={entry.category} onChange={(value) => updateEntry('skills', index, 'category', value)} />
            <TextField label="Skills — comma separated" value={entry.items.join(', ')} onChange={(value) => updateEntry('skills', index, 'items', value.split(',').map((item) => item.trim()).filter(Boolean))} />
          </div>)}
          {profile.skills.length === 0 && <p className="empty-note">No skills categories in this resume.</p>}
        </div>

        {error && <p className="field-error">{error}</p>}
        <div className="editor-actions">
          <button type="button" className="btn-ghost" onClick={onBack} disabled={loading}>Back to diagnosis</button>
          <button type="submit" className="btn-primary" disabled={loading}>{loading ? <><span className="button-spinner" aria-hidden="true" />Saving and rescanning…</> : 'Approve, rescan, and save version'}</button>
        </div>
      </form>
    </section>
  )
}
