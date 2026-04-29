import type { BowelMovement } from '../types'
import { startOfDay, formatDayHeader } from '../types'
import EntryRow from './EntryRow'

interface Props {
  movements: BowelMovement[]
  onDelete: (id: string) => void
}

export default function HistoryView({ movements, onDelete }: Props) {
  // Group by calendar day, newest first
  const grouped: { dayTs: number; items: BowelMovement[] }[] = []
  const map = new Map<number, BowelMovement[]>()

  for (const m of [...movements].sort((a, b) => b.timestamp - a.timestamp)) {
    const key = startOfDay(m.timestamp)
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(m)
  }

  for (const [dayTs, items] of map) {
    grouped.push({ dayTs, items })
  }

  grouped.sort((a, b) => b.dayTs - a.dayTs)

  if (grouped.length === 0) {
    return (
      <div className="view">
        <div className="view-header">
          <h1 className="view-title">History</h1>
        </div>
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          <h3>No history yet</h3>
          <p>Logged entries will appear here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="view">
      <div className="view-header">
        <h1 className="view-title">History</h1>
      </div>

      {grouped.map(({ dayTs, items }) => {
        const count = items.length
        const hasBlood = items.some(m => m.hasBlood)
        const hasMucus = items.some(m => m.hasMucus)
        const countCls = count >= 8 ? 'danger' : count >= 5 ? 'warning' : 'normal'

        return (
          <div key={dayTs} className="day-group">
            <div className="day-header">
              <span className="day-title">{formatDayHeader(dayTs)}</span>
              {hasBlood && <span style={{ fontSize: 14 }}>🩸</span>}
              {hasMucus && <span style={{ fontSize: 14 }}>💧</span>}
              <span className={`day-count ${countCls}`}>{count}</span>
            </div>
            <div className="entry-list">
              {items.map(m => (
                <EntryRow key={m.id} movement={m} onDelete={onDelete} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
