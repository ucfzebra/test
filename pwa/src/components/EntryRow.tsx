import type { BowelMovement } from '../types'
import { BRISTOL_TYPES, URGENCY_LABELS, bristolColor, urgencyColor, urgencyBg, formatTime } from '../types'

interface Props {
  movement: BowelMovement
  onDelete: (id: string) => void
}

export default function EntryRow({ movement, onDelete }: Props) {
  const bristol = BRISTOL_TYPES.find(b => b.id === movement.consistency)
  const urg = movement.urgency

  return (
    <div className="entry-row">
      <span className="entry-time">{formatTime(movement.timestamp)}</span>
      <div className="entry-divider" />
      <div className="entry-body">
        <div className="entry-bristol">
          <span style={{ color: bristolColor(movement.consistency) }}>Bristol {movement.consistency}</span>
          {bristol && <span className="entry-bristol-desc"> · {bristol.description}</span>}
        </div>
        <div className="entry-badges">
          <span
            className="badge"
            style={{ color: urgencyColor(urg), background: urgencyBg(urg) }}
          >
            {URGENCY_LABELS[urg - 1]}
          </span>
          {movement.hasBlood && (
            <span className="badge" style={{ color: '#b91c1c', background: '#fee2e2' }}>
              🩸 Blood
            </span>
          )}
          {movement.hasMucus && (
            <span className="badge" style={{ color: '#9a3412', background: '#ffedd5' }}>
              💧 Mucus
            </span>
          )}
        </div>
        {movement.notes && <p className="entry-notes">{movement.notes}</p>}
      </div>
      <button
        className="entry-delete"
        onClick={() => onDelete(movement.id)}
        aria-label="Delete entry"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
          <path d="M10 11v6M14 11v6" />
          <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
        </svg>
      </button>
    </div>
  )
}
