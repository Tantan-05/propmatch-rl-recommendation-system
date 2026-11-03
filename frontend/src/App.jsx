// src/App.jsx
import { useState, useCallback } from 'react'
import PreferenceForm from './components/PreferenceForm'
import PropertyCard  from './components/PropertyCard'
import { fetchRecommendations } from './api'

export default function App() {
  const [loading, setLoading]             = useState(false)
  const [recommendations, setRecommendations] = useState(null)  // null = never submitted
  const [error, setError]                 = useState(null)

  const handleSubmit = useCallback(async (prefs) => {
    setLoading(true)
    setError(null)
    setRecommendations(null)

    try {
      const data = await fetchRecommendations(prefs)
      setRecommendations(data.recommendations)
    } catch (err) {
      setError(err.message || 'An unexpected error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <div className="app-wrapper">
      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="app-header" role="banner">
        <div className="logo-icon" aria-hidden="true">🏠</div>
        <span className="brand">PropMatch</span>
        <span className="tagline">— AI Property Recommendations</span>
      </header>

      {/* ── Main ───────────────────────────────────────────────── */}
      <main className="main-content" role="main">

        {/* Hero */}
        <section className="hero">
          <h1>Find Your Perfect Mumbai Property</h1>
          <p>
            Enter your preferences below. Our reinforcement-learning model
            scores every listing against your requirements and returns the
            four best-matched properties.
          </p>
        </section>

        {/* Preference form */}
        <PreferenceForm onSubmit={handleSubmit} loading={loading} />

        {/* Error banner */}
        {error && (
          <div className="error-banner" role="alert" aria-live="assertive">
            <span className="err-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Results */}
        {recommendations !== null && (
          <section aria-label="Recommendation results">
            <div className="results-header">
              <h2>Recommended Properties</h2>
              <span className="result-count">
                {recommendations.length} result{recommendations.length !== 1 ? 's' : ''}
              </span>
            </div>

            {recommendations.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔎</div>
                <h3>No properties found</h3>
                <p>Try relaxing your area range, budget, or locality preference.</p>
              </div>
            ) : (
              <>
                <div className="results-grid">
                  {recommendations.map((rec, i) => (
                    <PropertyCard key={rec.title + i} rec={rec} rank={i + 1} />
                  ))}
                </div>

                <p className="score-note">
                  <strong>About the model score:</strong> Each score (0–1) indicates
                  how well the property matches your preferences according to the
                  trained reward-prediction model. A higher score means a stronger
                  predicted match — it is not a guarantee of satisfaction and does not
                  reflect actual market valuation.
                </p>
              </>
            )}
          </section>
        )}

        {/* Pre-submission empty state */}
        {recommendations === null && !error && !loading && (
          <div className="empty-state">
            <div className="empty-icon">🏙️</div>
            <h3>Your recommendations will appear here</h3>
            <p>Fill in your preferences above and click <strong>Find My Properties</strong>.</p>
          </div>
        )}

      </main>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer className="app-footer">
        PropMatch · Powered by a trained RL reward-prediction model ·
        Scores are predicted suitability values, not purchase recommendations.
      </footer>
    </div>
  )
}
