// src/utils.js

/**
 * Format a number as Indian rupees with the Indian numbering system.
 * e.g. 10500000 → "₹1,05,00,000"
 */
export function formatINR(amount) {
  if (amount == null || isNaN(amount)) return '—'
  const rounded = Math.round(amount)
  // Indian locale formats to lakh/crore grouping
  return '₹' + rounded.toLocaleString('en-IN')
}

/**
 * Return a short human-readable label for a price.
 * e.g. 10500000 → "₹1.05 Cr"  |  850000 → "₹8.5 L"
 */
export function formatINRShort(amount) {
  if (amount == null || isNaN(amount)) return '—'
  if (amount >= 10_000_000) {
    return '₹' + (amount / 10_000_000).toFixed(2).replace(/\.?0+$/, '') + ' Cr'
  }
  if (amount >= 100_000) {
    return '₹' + (amount / 100_000).toFixed(1).replace(/\.0$/, '') + ' L'
  }
  return formatINR(amount)
}

/**
 * Score colour class: high ≥ 0.85, mid ≥ 0.60, else low.
 */
export function scoreClass(score) {
  if (score >= 0.85) return 'high'
  if (score >= 0.60) return 'mid'
  return 'low'
}

/**
 * Title-case a lowercase string.
 */
export function titleCase(str) {
  return String(str).replace(/\b\w/g, c => c.toUpperCase())
}
