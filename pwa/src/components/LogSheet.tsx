import { useState } from 'react'
import type { BowelMovement } from '../types'
import { BRISTOL_TYPES, URGENCY_LABELS, bristolColor, urgencyColor, formatDateTimeLocal } from '../types'

interface Props {
  onSave: (m: BowelMovement) => void
  onClose: () => void
}

export default function LogSheet({ onSave, onClose }: Props) {
  const [timestamp, setTimestamp] = useState(() => formatDateTimeLocal(new Date()))
  const [consistency, setConsistency] = useState(4)
  const [urgency, setUrgency] = useState(1)
  const [hasBlood, setHasBlood] = useState(false)
  const [hasMucus, setHasMucus] = useState(false)
  const [notes, setNotes] = useState('')

  function handleSave() {
    onSave({
      id: crypto.randomUUID(),
      timestamp: new Date(timestamp).getTime(),
      consistency,
      urgency,
      hasBlood,
      hasMucus,
      notes: notes.trim(),
    })
  }

  return (
    <>
      <div className="sheet-backdrop" onClick={onClose} />
      <div className="sheet" role="dialog" aria-modal="true" aria-label="Log entry">
        <div className="sheet-handle" />
        <div className="sheet-header">
          <button className="sheet-cancel" onClick={onClose}>Cancel</button>
          <span className="sheet-title">Log Entry</span>
          <button className="sheet-save" onClick={handleSave}>Save</button>
        </div>

        <div className="sheet-body">
          {/* Time */}
          <section className="form-section">
            <label className="form-label" htmlFor="ts">Time</label>
            <input
              id="ts"
              type="datetime-local"
              className="datetime-input"
              value={timestamp}
              onChange={e => setTimestamp(e.target.value)}
            />
          </section>

          {/* Bristol */}
          <section className="form-section">
            <p className="form-label">Consistency — Bristol Stool Scale</p>
            <div className="bristol-list">
              {BRISTOL_TYPES.map(type => (
                <button
                  key={type.id}
                  className={`bristol-option${consistency === type.id ? ' selected' : ''}`}
                  onClick={() => setConsistency(type.id)}
                >
                  <span
                    className="bristol-num"
                    style={{ color: bristolColor(type.id), background: bristolColor(type.id) + '22' }}
                  >
                    {type.id}
                  </span>
                  <span className="bristol-info">
                    <span className="bristol-name">{type.name}</span>
                    <span className="bristol-desc">{type.description}</span>
                  </span>
                  {consistency === type.id && (
                    <svg className="bristol-check" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
            <p className="form-footer">1–2: constipation · 3–4: normal · 5–7: diarrhea</p>
          </section>

          {/* Urgency */}
          <section className="form-section">
            <p className="form-label">Urgency</p>
            <div className="urgency-grid">
              {([1, 2, 3, 4, 5] as const).map(level => {
                const active = urgency === level
                const col = urgencyColor(level)
                return (
                  <button
                    key={level}
                    className="urgency-btn"
                    style={active
                      ? { background: col, color: '#fff', borderColor: col }
                      : { color: col, borderColor: col + '55', background: col + '11' }
                    }
                    onClick={() => setUrgency(level)}
                  >
                    <span className="urgency-num">{level}</span>
                    <span className="urgency-lbl">{URGENCY_LABELS[level - 1]}</span>
                  </button>
                )
              })}
            </div>
          </section>

          {/* Symptoms */}
          <section className="form-section">
            <p className="form-label">Symptoms</p>
            <div className="toggle-list">
              <label className={`toggle-row blood${hasBlood ? ' checked' : ''}`}>
                <span className="toggle-label-text">🩸 Blood present</span>
                <input
                  type="checkbox"
                  checked={hasBlood}
                  onChange={e => setHasBlood(e.target.checked)}
                />
              </label>
              <label className={`toggle-row mucus${hasMucus ? ' checked' : ''}`}>
                <span className="toggle-label-text">💧 Mucus present</span>
                <input
                  type="checkbox"
                  checked={hasMucus}
                  onChange={e => setHasMucus(e.target.checked)}
                />
              </label>
            </div>
          </section>

          {/* Notes */}
          <section className="form-section">
            <label className="form-label" htmlFor="notes">Notes (optional)</label>
            <textarea
              id="notes"
              className="notes-input"
              rows={3}
              placeholder="e.g. after meal, cramping…"
              value={notes}
              onChange={e => setNotes(e.target.value)}
            />
          </section>
        </div>
      </div>
    </>
  )
}
