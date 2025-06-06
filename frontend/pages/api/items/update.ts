import type { NextApiRequest, NextApiResponse } from 'next'
import { items } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'PUT') return res.status(405).end()
  const { id, name, quantity, min_par, category_id, department_id, stock_code, status } = req.body
  const idx = items.findIndex(i => i.id === Number(id))
  if (idx === -1) return res.status(404).end()
  items[idx] = { ...items[idx], name, quantity: Number(quantity), min_par: Number(min_par), category_id: Number(category_id), department_id: Number(department_id), stock_code, status }
  res.status(200).json(items[idx])
}
