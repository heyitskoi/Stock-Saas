import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen p-4 text-center">
      <div>
        <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
        <p className="mb-6 text-muted-foreground">Sorry, the page you are looking for does not exist.</p>
        <Link href="/" className="text-blue-600 hover:underline">
          Go back home
        </Link>
      </div>
    </div>
  )
}
