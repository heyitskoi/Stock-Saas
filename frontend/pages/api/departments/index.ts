import type { NextApiRequest, NextApiResponse } from 'next'
import { departments } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    res.status(200).json(departments)
  } else if (req.method === 'POST') {
    const { name, icon } = req.body
    const id = departments.length ? Math.max(...departments.map(d => d.id)) + 1 : 1
    const dept = { id, name, icon }
    departments.push(dept)
    res.status(200).json(dept)
  } else {
    res.status(405).end()
  }
}
