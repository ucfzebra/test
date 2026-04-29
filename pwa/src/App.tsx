import { useState, useEffect, useCallback } from 'react'
import { getAll, addMovement, deleteMovement } from './db'
import type { BowelMovement } from './types'
import TodayView from './components/TodayView'
import HistoryView from './components/HistoryView'
import StatsView from './components/StatsView'
import LogSheet from './components/LogSheet'

type Tab = 'today' | 'history' | 'stats'

export default function App() {
  const [movements, setMovements] = useState<BowelMovement[]>([])
  const [tab, setTab] = useState<Tab>('today')
  const [showLog, setShowLog] = useState(false)

  const reload = useCallback(async () => {
    setMovements(await getAll())
  }, [])

  useEffect(() => { reload() }, [reload])

  async function handleSave(m: BowelMovement) {
    await addMovement(m)
    await reload()
    setShowLog(false)
  }

  async function handleDelete(id: string) {
    await deleteMovement(id)
    await reload()
  }

  return (
    <div className="app">
      <main className="main-content">
        {tab === 'today' && (
          <TodayView
            movements={movements}
            onAdd={() => setShowLog(true)}
            onDelete={handleDelete}
          />
        )}
        {tab === 'history' && (
          <HistoryView movements={movements} onDelete={handleDelete} />
        )}
        {tab === 'stats' && (
          <StatsView movements={movements} />
        )}
      </main>

      <nav className="tab-bar">
        <TabBtn icon={<IconHome />} label="Today" active={tab === 'today'} onClick={() => setTab('today')} />
        <TabBtn icon={<IconCal />} label="History" active={tab === 'history'} onClick={() => setTab('history')} />
        <TabBtn icon={<IconChart />} label="Trends" active={tab === 'stats'} onClick={() => setTab('stats')} />
      </nav>

      {showLog && <LogSheet onSave={handleSave} onClose={() => setShowLog(false)} />}
    </div>
  )
}

function TabBtn({ icon, label, active, onClick }: {
  icon: React.ReactNode
  label: string
  active: boolean
  onClick: () => void
}) {
  return (
    <button className={`tab-btn${active ? ' active' : ''}`} onClick={onClick}>
      {icon}
      <span>{label}</span>
    </button>
  )
}

function IconHome() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  )
}

function IconCal() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  )
}

function IconChart() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  )
}
