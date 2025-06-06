import type { NextApiRequest, NextApiResponse } from 'next'
import { categories } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    res.status(200).json(categories)
  } else if (req.method === 'POST') {
    const { name, department_id, icon } = req.body
    const id = categories.length ? Math.max(...categories.map(c => c.id)) + 1 : 1
    const cat = { id, name, department_id: Number(department_id), icon }
    categories.push(cat)
    res.status(200).json(cat)
  } else {
    res.status(405).end()
  }
}
