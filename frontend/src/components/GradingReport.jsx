const CATEGORY_LABELS = {
  technical_skills_match: 'Technical skills match',
  experience_relevance: 'Experience relevance',
  keyword_optimization: 'Keyword optimization',
  action_verb_strength: 'Action verb strength',
  quantifiable_impact: 'Quantifiable impact',
}

function scoreTone(score) {
  if (score >= 75) return 'tone-good'
  if (score >= 50) return 'tone-mid'
  return 'tone-low'
}

function Gauge({ label, score }) {
  return (
    <div className="gauge-row">
      <span className="gauge-label">{label}</span>
      <div className="gauge-track">
        <div className={`gauge-fill ${scoreTone(score)}`} style={{ width: `${score}%` }} />
        <span className="gauge-tick" style={{ left: '25%' }} />
        <span className="gauge-tick" style={{ left: '50%' }} />
        <span className="gauge-tick" style={{ left: '75%' }} />
      </div>
      <span className="gauge-value">{String(score).padStart(2, '0')}</span>
    </div>
  )
}

function Annotation({ kind, category, children }) {
  return (
    <div className={`annotation annotation-${kind}`}>
      <span className="annotation-mark" aria-hidden="true">{kind === 'strength' ? '✓' : '›'}</span>
      <div>
        <span className="annotation-category">{category}</span>
        {children}
      </div>
    </div>
  )
}

export default function GradingReport({ result, onRestart }) {
  const {
    overall_score: overall,
    score_breakdown: breakdown,
    strengths,
    improvements,
    missing_keywords: missingKeywords,
    ats_flags: atsFlags,
  } = result

  return (
    <section className="panel report">
      <div className="report-header">
        <div>
          <p className="eyebrow">Diagnosis</p>
          <h2 className="panel-title">Overall match</h2>
        </div>
        <div className={`score-badge ${scoreTone(overall)}`}>
          <span className="score-number">{overall}</span>
          <span className="score-max">/100</span>
        </div>
      </div>

      <div className="gauges">
        {Object.entries(breakdown).map(([key, value]) => (
          <Gauge key={key} label={CATEGORY_LABELS[key] || key} score={value} />
        ))}
      </div>

      <div className="report-columns">
        <div>
          <h3 className="report-subhead">What's working</h3>
          {strengths.map((s, i) => (
            <Annotation key={i} kind="strength" category={s.category}>
              <p className="annotation-body">{s.observation}</p>
              <p className="annotation-evidence">&ldquo;{s.evidence}&rdquo;</p>
            </Annotation>
          ))}
        </div>
        <div>
          <h3 className="report-subhead">Redline notes</h3>
          {improvements.map((imp, i) => (
            <Annotation key={i} kind="issue" category={imp.category}>
              <p className="annotation-body">{imp.issue}</p>
              <p className="annotation-fix">
                <span>Rewrite:</span> {imp.example_rewrite}
              </p>
            </Annotation>
          ))}
        </div>
      </div>

      {missingKeywords.length > 0 && (
        <div className="chip-block">
          <h3 className="report-subhead">Missing from the posting</h3>
          <div className="chips">
            {missingKeywords.map((kw) => (
              <span key={kw} className="chip">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {atsFlags.length > 0 && (
        <div className="chip-block">
          <h3 className="report-subhead">ATS parsing risks</h3>
          <ul className="flag-list">
            {atsFlags.map((flag, i) => (
              <li key={i}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="report-actions">
        <button className="btn-primary" onClick={onRestart}>
          Start over
        </button>
      </div>
    </section>
  )
}
