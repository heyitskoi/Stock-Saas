import type { NextApiRequest, NextApiResponse } from 'next'
import { items } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { name, quantity, min_par, category_id, department_id, stock_code, status } = req.body
  const id = items.length ? Math.max(...items.map(i => i.id)) + 1 : 1
  const item = { id, name, quantity: Number(quantity), min_par: Number(min_par), category_id: Number(category_id), department_id: Number(department_id), stock_code, status: status || 'available' }
  items.push(item)
  res.status(200).json(item)
}
