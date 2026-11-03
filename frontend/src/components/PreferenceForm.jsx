// src/components/PreferenceForm.jsx
import { useState } from 'react'
import {
  CITIES, PROPERTY_TYPES, FURNISHED_OPTIONS, LOCALITIES, DEFAULT_PREFS,
} from '../constants'

function Field({ label, id, error, children }) {
  return (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      {children}
      {error && <span className="field-error">{error}</span>}
    </div>
  )
}

function NumberInput({ id, value, onChange, min, max, step = 1, placeholder }) {
  return (
    <input
      id={id}
      type="number"
      value={value}
      onChange={e => onChange(e.target.value)}
      min={min}
      max={max}
      step={step}
      placeholder={placeholder}
      autoComplete="off"
    />
  )
}

function SelectInput({ id, value, onChange, options }) {
  return (
    <select id={id} value={value} onChange={e => onChange(e.target.value)}>
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  )
}

// Validate form values; return object of field → error string (empty = ok)
function validate(f) {
  const errs = {}
  if (!f.budget_max || Number(f.budget_max) <= 0)
    errs.budget_max = 'Budget must be greater than 0'
  if (!f.min_area || Number(f.min_area) < 0)
    errs.min_area = 'Minimum area must be ≥ 0'
  if (!f.max_area || Number(f.max_area) < 0)
    errs.max_area = 'Maximum area must be ≥ 0'
  if (Number(f.min_area) > Number(f.max_area))
    errs.max_area = 'Max area must be ≥ min area'
  if (!f.bedroom_pref || Number(f.bedroom_pref) < 0)
    errs.bedroom_pref = 'Must be ≥ 0'
  if (!f.bathroom_pref || Number(f.bathroom_pref) < 0)
    errs.bathroom_pref = 'Must be ≥ 0'
  if (Number(f.balcony_pref) < 0)
    errs.balcony_pref = 'Must be ≥ 0'
  if (!f.max_age || Number(f.max_age) < 0)
    errs.max_age = 'Must be ≥ 0'
  return errs
}

export default function PreferenceForm({ onSubmit, loading }) {
  const [form, setForm] = useState({ ...DEFAULT_PREFS })
  const [touched, setTouched] = useState({})
  const [submitAttempted, setSubmitAttempted] = useState(false)

  const set = (key) => (val) => {
    setForm(f => ({ ...f, [key]: val }))
    setTouched(t => ({ ...t, [key]: true }))
  }

  const errs = validate(form)
  const showErr = (key) =>
    (touched[key] || submitAttempted) ? errs[key] : undefined

  const handleSubmit = (e) => {
    e.preventDefault()
    setSubmitAttempted(true)
    if (Object.keys(errs).length > 0) return

    // Build the payload matching inference.py exactly
    onSubmit({
      budget_max:          Number(form.budget_max),
      min_area:            Number(form.min_area),
      max_area:            Number(form.max_area),
      bedroom_pref:        Number(form.bedroom_pref),
      bathroom_pref:       Number(form.bathroom_pref),
      balcony_pref:        Number(form.balcony_pref),
      max_age:             Number(form.max_age),
      locality_pref:       String(form.locality_pref).toLowerCase(),
      city_pref:           String(form.city_pref).toLowerCase(),
      property_type_pref:  String(form.property_type_pref).toLowerCase(),
      furnished_pref:      String(form.furnished_pref).toLowerCase(),
    })
  }

  const handleReset = () => {
    setForm({ ...DEFAULT_PREFS })
    setTouched({})
    setSubmitAttempted(false)
  }

  return (
    <form className="form-card" onSubmit={handleSubmit} noValidate>
      <h2>Your Preferences</h2>

      <div className="form-grid">

        {/* --- Budget & Area --- */}
        <div className="form-section-label">Budget &amp; Area</div>

        <Field label="Budget (₹)" id="budget_max" error={showErr('budget_max')}>
          <NumberInput
            id="budget_max" value={form.budget_max}
            onChange={set('budget_max')} min={0} step={100000}
            placeholder="e.g. 15000000"
          />
        </Field>

        <Field label="Min Area (sq.ft)" id="min_area" error={showErr('min_area')}>
          <NumberInput
            id="min_area" value={form.min_area}
            onChange={set('min_area')} min={0}
            placeholder="e.g. 900"
          />
        </Field>

        <Field label="Max Area (sq.ft)" id="max_area" error={showErr('max_area')}>
          <NumberInput
            id="max_area" value={form.max_area}
            onChange={set('max_area')} min={0}
            placeholder="e.g. 1400"
          />
        </Field>

        {/* --- Configuration --- */}
        <div className="form-section-label">Configuration</div>

        <Field label="Bedrooms (BHK)" id="bedroom_pref" error={showErr('bedroom_pref')}>
          <NumberInput
            id="bedroom_pref" value={form.bedroom_pref}
            onChange={set('bedroom_pref')} min={0} max={15}
          />
        </Field>

        <Field label="Bathrooms" id="bathroom_pref" error={showErr('bathroom_pref')}>
          <NumberInput
            id="bathroom_pref" value={form.bathroom_pref}
            onChange={set('bathroom_pref')} min={0} max={15}
          />
        </Field>

        <Field label="Balconies" id="balcony_pref" error={showErr('balcony_pref')}>
          <NumberInput
            id="balcony_pref" value={form.balcony_pref}
            onChange={set('balcony_pref')} min={0} max={15}
          />
        </Field>

        {/* --- Location & Type --- */}
        <div className="form-section-label">Location &amp; Property Type</div>

        <Field label="Preferred Locality" id="locality_pref">
          <select
            id="locality_pref"
            value={form.locality_pref}
            onChange={e => set('locality_pref')(e.target.value)}
          >
            {LOCALITIES.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </Field>

        <Field label="City" id="city_pref">
          <SelectInput
            id="city_pref" value={form.city_pref}
            onChange={set('city_pref')} options={CITIES}
          />
        </Field>

        <Field label="Property Type" id="property_type_pref">
          <SelectInput
            id="property_type_pref" value={form.property_type_pref}
            onChange={set('property_type_pref')} options={PROPERTY_TYPES}
          />
        </Field>

        {/* --- Condition --- */}
        <div className="form-section-label">Condition</div>

        <Field label="Furnishing" id="furnished_pref">
          <SelectInput
            id="furnished_pref" value={form.furnished_pref}
            onChange={set('furnished_pref')} options={FURNISHED_OPTIONS}
          />
        </Field>

        <Field label="Max Property Age (years)" id="max_age" error={showErr('max_age')}>
          <NumberInput
            id="max_age" value={form.max_age}
            onChange={set('max_age')} min={0} max={60}
            placeholder="e.g. 10"
          />
        </Field>

      </div>

      <div className="form-actions">
        <button
          type="button"
          className="btn-ghost"
          onClick={handleReset}
          disabled={loading}
          id="reset-btn"
        >
          Reset
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
          id="submit-btn"
        >
          {loading ? (
            <>
              <span className="spinner" />
              Searching…
            </>
          ) : (
            <>🔍 Find My Properties</>
          )}
        </button>
      </div>
    </form>
  )
}
