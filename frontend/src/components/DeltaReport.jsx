function DeltaBadge({ delta }) {
  const positive = delta > 0
  const flat = delta === 0
  const tone = flat ? 'tone-mid' : positive ? 'tone-good' : 'tone-low'
  const label = flat ? '±0' : positive ? `+${delta}` : `${delta}`
  return <span className={`delta-badge ${tone}`}>{label}</span>
}

export default function DeltaReport({ result, onRestart }) {
  const { score_delta: scoreDelta, category_deltas: categoryDeltas, resolved_issues: resolved, new_issues: newIssues, verdict } = result

  return (
    <section className="panel report">
      <div className="report-header">
        <div>
          <p className="eyebrow">Revision check</p>
          <h2 className="panel-title">Did it get stronger?</h2>
        </div>
        <DeltaBadge delta={scoreDelta} />
      </div>

      <p className="verdict">{verdict}</p>

      <div className="delta-grid">
        {categoryDeltas.map((c) => (
          <div key={c.category} className="delta-row">
            <span className="delta-category">{c.category.replaceAll('_', ' ')}</span>
            <span className="delta-values">
              {c.previous} → {c.current}
            </span>
            <DeltaBadge delta={c.delta} />
          </div>
        ))}
      </div>

      <div className="report-columns">
        <div>
          <h3 className="report-subhead">Resolved</h3>
          {resolved.length === 0 && <p className="empty-note">Nothing resolved yet.</p>}
          {resolved.map((issue, i) => (
            <div key={i} className="annotation annotation-strength">
              <span className="annotation-mark" aria-hidden="true">✓</span>
              <p className="annotation-body">{issue}</p>
            </div>
          ))}
        </div>
        <div>
          <h3 className="report-subhead">New issues</h3>
          {newIssues.length === 0 && <p className="empty-note">No new issues introduced.</p>}
          {newIssues.map((issue, i) => (
            <div key={i} className="annotation annotation-issue">
              <span className="annotation-mark" aria-hidden="true">›</span>
              <p className="annotation-body">{issue}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="report-actions">
        <button className="btn-primary" onClick={onRestart}>
          Start a new review
        </button>
      </div>
    </section>
  )
}
