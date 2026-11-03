// src/components/PropertyCard.jsx
import { formatINR, formatINRShort, scoreClass, titleCase } from '../utils'

export default function PropertyCard({ rec, rank }) {
  const sc = scoreClass(rec.predicted_reward)
  const scorePercent = Math.round(rec.predicted_reward * 100)

  return (
    <div className="property-card" role="article" aria-label={`Recommendation ${rank}: ${rec.title}`}>
      <div className={`card-rank-bar rank-${rank}`} />

      <div className="card-body">
        <div className="card-rank-badge">
          <span>#{rank}</span>
          <span>{rank === 1 ? 'Best Match' : rank === 2 ? 'Great Match' : 'Good Match'}</span>
        </div>

        <h3 className="card-title">{rec.title}</h3>

        <div className="card-price">
          {formatINRShort(rec.price)}
          <span style={{ fontSize: '.75rem', fontWeight: 400, color: 'var(--text-secondary)', marginLeft: 6 }}>
            ({formatINR(rec.price)})
          </span>
        </div>

        <div className="card-specs">
          <span className="spec-chip">🛏 {rec.bedroom_num % 1 === 0 ? rec.bedroom_num.toFixed(0) : rec.bedroom_num} BHK</span>
          <span className="spec-chip">🚿 {rec.bathroom_num % 1 === 0 ? rec.bathroom_num.toFixed(0) : rec.bathroom_num} Bath</span>
          {rec.balcony_num > 0 && (
            <span className="spec-chip">🪟 {rec.balcony_num % 1 === 0 ? rec.balcony_num.toFixed(0) : rec.balcony_num} Balcony</span>
          )}
          <span className="spec-chip">📐 {Math.round(rec.area).toLocaleString('en-IN')} sq.ft</span>
        </div>

        <div className="card-specs">
          <span className="spec-chip">{titleCase(rec.property_type)}</span>
          <span className="spec-chip">{titleCase(rec.furnished)}</span>
          {rec.age > 0 && <span className="spec-chip">{rec.age % 1 === 0 ? rec.age.toFixed(0) : rec.age} yr old</span>}
          {rec.age === 0 && <span className="spec-chip">New</span>}
        </div>

        <div className="card-location">
          <span className="pin">📍</span>
          {titleCase(rec.locality)}, {titleCase(rec.city)}
        </div>

        <hr className="card-divider" />

        <div className="score-row">
          <span className="score-label">Model score</span>
          <span className={`score-value ${sc}`}>{rec.predicted_reward.toFixed(4)}</span>
        </div>
        <div className="score-bar-wrap" title={`${scorePercent}% match score`}>
          <div
            className={`score-bar-fill ${sc}`}
            style={{ width: `${scorePercent}%` }}
          />
        </div>
      </div>
    </div>
  )
}
