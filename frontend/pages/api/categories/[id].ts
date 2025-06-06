import type { NextApiRequest, NextApiResponse } from 'next'
import { categories } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const id = parseInt(req.query.id as string)
  const idx = categories.findIndex(c => c.id === id)
  if (idx === -1) {
    res.status(404).end()
    return
  }
  if (req.method === 'PUT') {
    const { name, department_id, icon } = req.body
    categories[idx] = { ...categories[idx], name, department_id: Number(department_id), icon }
    res.status(200).json(categories[idx])
  } else if (req.method === 'DELETE') {
    categories.splice(idx, 1)
    res.status(200).json({ success: true })
  } else {
    res.status(405).end()
  }
}
