import type { BowelMovement } from '../types'
import { startOfDay, formatTime } from '../types'
import EntryRow from './EntryRow'

interface Props {
  movements: BowelMovement[]
  onAdd: () => void
  onDelete: (id: string) => void
}

export default function TodayView({ movements, onAdd, onDelete }: Props) {
  const todayStart = startOfDay(Date.now())
  const today = movements
    .filter(m => m.timestamp >= todayStart)
    .sort((a, b) => b.timestamp - a.timestamp)

  const count = today.length
  const hasBlood = today.some(m => m.hasBlood)
  const hasMucus = today.some(m => m.hasMucus)
  const avgUrgency = count > 0
    ? (today.reduce((s, m) => s + m.urgency, 0) / count).toFixed(1)
    : null

  const countClass = count >= 8 ? 'danger' : count >= 5 ? 'warning' : 'normal'

  const dateLabel = new Date().toLocaleDateString([], {
    weekday: 'long', month: 'long', day: 'numeric',
  })

  return (
    <div className="view">
      <div className="view-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <h1 className="view-title">Today</h1>
            <p className="view-subtitle">{dateLabel}</p>
          </div>
          <button className="add-btn" onClick={onAdd} aria-label="Log movement">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Summary card */}
      <div className="card count-card">
        <div className="count-top">
          <div>
            <p className="count-label">Movements</p>
            <p className={`count-num ${countClass}`}>{count}</p>
          </div>
          <div className="count-badges">
            {hasBlood && (
              <span className="badge" style={{ color: '#b91c1c', background: '#fee2e2' }}>🩸 Blood</span>
            )}
            {hasMucus && (
              <span className="badge" style={{ color: '#9a3412', background: '#ffedd5' }}>💧 Mucus</span>
            )}
          </div>
        </div>
        {avgUrgency && (
          <div className="count-footer">
            Avg urgency: <strong>{avgUrgency}</strong> / 5
          </div>
        )}
      </div>

      {/* Entry list */}
      {today.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3>No entries yet today</h3>
          <p>Tap + to log a movement</p>
          <button className="fab" onClick={onAdd}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Log Movement
          </button>
        </div>
      ) : (
        <>
          <p className="section-header">Today's Log</p>
          <div className="entry-list">
            {today.map(m => (
              <EntryRow key={m.id} movement={m} onDelete={onDelete} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
