import type { NextApiRequest, NextApiResponse } from 'next'
import { items } from '../mock-data'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    res.status(200).json(items)
  } else {
    res.status(405).end()
  }
}
