import { useState, useEffect } from 'react'

export function useIsMobile(threshold: number = 768) {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const update = () => setIsMobile(window.innerWidth <= threshold)
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [threshold])

  return isMobile
}
