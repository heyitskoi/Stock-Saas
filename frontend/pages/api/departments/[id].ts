import type { NextApiRequest, NextApiResponse } from 'next'
import { departments, categories } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const id = parseInt(req.query.id as string)
  const idx = departments.findIndex(d => d.id === id)
  if (idx === -1) {
    res.status(404).end()
    return
  }

  if (req.method === 'PUT') {
    const { name, icon } = req.body
    departments[idx] = { ...departments[idx], name, icon }
    res.status(200).json(departments[idx])
  } else if (req.method === 'DELETE') {
    departments.splice(idx, 1)
    for (let i = categories.length - 1; i >= 0; i--) {
      if (categories[i].department_id === id) categories.splice(i, 1)
    }
    res.status(200).json({ success: true })
  } else {
    res.status(405).end()
  }
}
