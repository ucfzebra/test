import type { BowelMovement } from '../types'
import { startOfDay, URGENCY_LABELS } from '../types'

interface Props {
  movements: BowelMovement[]
}

interface DayCount {
  label: string
  value: number
}

export default function StatsView({ movements }: Props) {
  if (movements.length === 0) {
    return (
      <div className="view">
        <div className="view-header">
          <h1 className="view-title">Trends</h1>
        </div>
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          <h3>No data yet</h3>
          <p>Log some entries to see your trends</p>
        </div>
      </div>
    )
  }

  // Last 7 days
  const days: DayCount[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    d.setHours(0, 0, 0, 0)
    const start = d.getTime()
    const end = start + 86400000
    const count = movements.filter(m => m.timestamp >= start && m.timestamp < end).length
    const label = i === 0 ? 'Today' : d.toLocaleDateString([], { weekday: 'narrow' })
    days.push({ label, value: count })
  }

  const activeDays = days.filter(d => d.value > 0)
  const dailyAvg = activeDays.length > 0
    ? (activeDays.reduce((s, d) => s + d.value, 0) / activeDays.length).toFixed(1)
    : '—'

  const total = movements.length
  const bloodCount = movements.filter(m => m.hasBlood).length
  const mucusCount = movements.filter(m => m.hasMucus).length
  const bloodPct = total > 0 ? Math.round((bloodCount / total) * 100) : 0
  const mucusPct = total > 0 ? Math.round((mucusCount / total) * 100) : 0

  const avgConsistency = total > 0
    ? (movements.reduce((s, m) => s + m.consistency, 0) / total).toFixed(1)
    : '—'

  const avgUrgencyNum = total > 0
    ? movements.reduce((s, m) => s + m.urgency, 0) / total
    : 0
  const avgUrgencyLabel = avgUrgencyNum > 0
    ? URGENCY_LABELS[Math.round(avgUrgencyNum) - 1]
    : '—'

  return (
    <div className="view">
      <div className="view-header">
        <h1 className="view-title">Trends</h1>
      </div>

      {/* 7-day chart */}
      <div className="chart-card">
        <p className="chart-title">Last 7 Days</p>
        <div className="chart-wrap">
          <BarChart data={days} />
        </div>
      </div>

      {/* Stat grid */}
      <div className="stats-grid">
        <StatCard icon="📊" label="Daily Avg" value={dailyAvg} sub="movements / day" />
        <StatCard
          icon="⚡"
          label="Avg Urgency"
          value={avgUrgencyLabel}
          sub={avgUrgencyNum > 0 ? `${avgUrgencyNum.toFixed(1)} / 5` : ''}
        />
        <StatCard
          icon="🩸"
          label="Blood"
          value={`${bloodPct}%`}
          sub={`${bloodCount} of ${total} entries`}
          highlight={bloodCount > 0 ? '#fee2e2' : undefined}
        />
        <StatCard
          icon="💧"
          label="Mucus"
          value={`${mucusPct}%`}
          sub={`${mucusCount} of ${total} entries`}
          highlight={mucusCount > 0 ? '#ffedd5' : undefined}
        />
        <StatCard icon="🫘" label="Avg Bristol" value={avgConsistency} sub="stool consistency" />
        <StatCard icon="📋" label="Total Logged" value={String(total)} sub="all time" />
      </div>
    </div>
  )
}

// ─── Bar Chart ───────────────────────────────────────────────────────────────

function BarChart({ data }: { data: DayCount[] }) {
  const max = Math.max(...data.map(d => d.value), 1)
  const H = 100
  const BAR_W = 32
  const GAP = 10
  const totalW = data.length * (BAR_W + GAP) - GAP

  function barColor(v: number) {
    if (v === 0) return '#e2e8f0'
    if (v >= 8) return '#ef4444'
    if (v >= 5) return '#f97316'
    return '#0ea5e9'
  }

  return (
    <svg
      width={totalW}
      height={H + 28}
      viewBox={`0 0 ${totalW} ${H + 28}`}
      style={{ display: 'block', minWidth: totalW }}
    >
      {data.map((d, i) => {
        const barH = Math.max((d.value / max) * H, d.value > 0 ? 4 : 2)
        const x = i * (BAR_W + GAP)
        const y = H - barH
        const col = barColor(d.value)
        return (
          <g key={i}>
            <rect x={x} y={y} width={BAR_W} height={barH} rx={5} fill={col} />
            {d.value > 0 && (
              <text x={x + BAR_W / 2} y={y - 5} textAnchor="middle" fontSize={11} fontWeight="700" fill={col}>
                {d.value}
              </text>
            )}
            <text x={x + BAR_W / 2} y={H + 18} textAnchor="middle" fontSize={11} fill="#94a3b8" fontWeight="500">
              {d.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

// ─── Stat Card ───────────────────────────────────────────────────────────────

function StatCard({ icon, label, value, sub, highlight }: {
  icon: string
  label: string
  value: string
  sub?: string
  highlight?: string
}) {
  return (
    <div className="stat-card" style={highlight ? { background: highlight } : undefined}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  )
}
