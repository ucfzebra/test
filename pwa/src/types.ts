export interface BowelMovement {
  id: string
  timestamp: number  // Unix ms
  consistency: number  // 1–7 Bristol
  urgency: number      // 1–5
  hasBlood: boolean
  hasMucus: boolean
  notes: string
}

export const BRISTOL_TYPES = [
  { id: 1, name: 'Type 1', description: 'Separate hard lumps' },
  { id: 2, name: 'Type 2', description: 'Lumpy, sausage-like' },
  { id: 3, name: 'Type 3', description: 'Sausage with cracks' },
  { id: 4, name: 'Type 4', description: 'Smooth, soft sausage' },
  { id: 5, name: 'Type 5', description: 'Soft blobs, clear-cut' },
  { id: 6, name: 'Type 6', description: 'Fluffy, mushy pieces' },
  { id: 7, name: 'Type 7', description: 'Watery, no solid pieces' },
] as const

export const URGENCY_LABELS = ['None', 'Mild', 'Moderate', 'High', 'Extreme']

export function bristolColor(type: number): string {
  if (type <= 2) return '#92400e'
  if (type <= 4) return '#15803d'
  if (type <= 6) return '#c2410c'
  return '#b91c1c'
}

export function urgencyColor(level: number): string {
  return ['', '#15803d', '#854d0e', '#c2410c', '#b91c1c', '#7e22ce'][level] ?? '#64748b'
}

export function urgencyBg(level: number): string {
  return ['', '#dcfce7', '#fef9c3', '#ffedd5', '#fee2e2', '#f3e8ff'][level] ?? '#f1f5f9'
}

export function startOfDay(ts: number): number {
  const d = new Date(ts)
  d.setHours(0, 0, 0, 0)
  return d.getTime()
}

export function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

export function formatDayHeader(ts: number): string {
  const d = new Date(ts)
  const today = new Date()
  const yesterday = new Date()
  yesterday.setDate(today.getDate() - 1)
  if (d.toDateString() === today.toDateString()) return 'Today'
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return d.toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' })
}

export function formatDateTimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}
