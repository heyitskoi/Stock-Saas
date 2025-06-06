import type { NextApiRequest, NextApiResponse } from 'next'
import { items } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'DELETE') return res.status(405).end()
  const { id } = req.body
  const idx = items.findIndex(i => i.id === Number(id))
  if (idx === -1) return res.status(404).end()
  items.splice(idx, 1)
  res.status(200).json({ success: true })
}
