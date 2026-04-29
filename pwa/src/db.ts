import { openDB } from 'idb'
import type { BowelMovement } from './types'

const DB = 'bowel-tracker'
const STORE = 'movements'

const db = openDB(DB, 1, {
  upgrade(database) {
    const store = database.createObjectStore(STORE, { keyPath: 'id' })
    store.createIndex('by-timestamp', 'timestamp')
  },
})

export async function getAll(): Promise<BowelMovement[]> {
  return (await db).getAllFromIndex(STORE, 'by-timestamp')
}

export async function addMovement(m: BowelMovement): Promise<void> {
  await (await db).add(STORE, m)
}

export async function deleteMovement(id: string): Promise<void> {
  await (await db).delete(STORE, id)
}
