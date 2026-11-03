// src/api.js
// All API calls go through /api (proxied to backend by Vite dev server).

const BASE = '/api'

/**
 * POST /api/recommendations
 * Sends user preferences; returns { recommendations, count }.
 * Throws an Error with a user-friendly message on failure.
 */
export async function fetchRecommendations(prefs) {
  const res = await fetch(`${BASE}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prefs),
  })

  if (!res.ok) {
    let detail = `Server error (${res.status})`
    try {
      const body = await res.json()
      detail = body.detail || detail
      // Pydantic validation error is an array of error objects
      if (Array.isArray(detail)) {
        detail = detail.map(e => e.msg || JSON.stringify(e)).join(' • ')
      }
    } catch (_) { /* ignore json parse failure */ }
    throw new Error(detail)
  }

  return res.json()
}

/**
 * GET /api/health
 * Returns { status, assets, message }.
 */
export async function fetchHealth() {
  const res = await fetch(`${BASE}/health`)
  if (!res.ok) throw new Error(`Health check failed (${res.status})`)
  return res.json()
}
