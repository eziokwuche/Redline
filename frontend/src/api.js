const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

async function extractError(res) {
  try {
    const data = await res.json()
    return data.detail || `Request failed (${res.status})`
  } catch {
    return `Request failed (${res.status})`
  }
}

export async function uploadResume(file, sessionId) {
  const form = new FormData()
  form.append('file', file)

  const url = new URL(`${BASE}/resumes`)
  if (sessionId) url.searchParams.set('session_id', sessionId)

  const res = await fetch(url, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await extractError(res))
  return res.json()
}

export async function createJobDescription(payload, sessionId) {
  const url = new URL(`${BASE}/job-descriptions`)
  if (sessionId) url.searchParams.set('session_id', sessionId)

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await extractError(res))
  return res.json()
}

export async function gradeResume(resumeId, jobDescriptionId) {
  const res = await fetch(`${BASE}/grade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_id: resumeId, job_description_id: jobDescriptionId }),
  })
  if (!res.ok) throw new Error(await extractError(res))
  return res.json()
}

export async function rescanResume(resumeId, profile, jobDescriptionId, targetCompany) {
  const res = await fetch(`${BASE}/resumes/${resumeId}/rescan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      profile,
      job_description_id: jobDescriptionId,
      ...(targetCompany ? { target_company: targetCompany } : {}),
    }),
  })
  if (!res.ok) throw new Error(await extractError(res))
  return res.json()
}

export async function compileResume(resumeId) {
  const res = await fetch(`${BASE}/resumes/${resumeId}/compile`, { method: 'POST' })
  if (!res.ok) throw new Error(await extractError(res))
  return res.blob()
}

export async function compareVersions(previousGradingId, currentGradingId) {
  const res = await fetch(`${BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      previous_grading_id: previousGradingId,
      current_grading_id: currentGradingId,
    }),
  })
  if (!res.ok) throw new Error(await extractError(res))
  return res.json()
}
