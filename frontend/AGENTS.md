# frontend-agent Instructions

This directory contains the Next.js interface managed by the **frontend-agent**.

## Responsibilities
- Build pages for login, inventory dashboard and item management.
- Use components from V0.dev or simple React components.
- Integrate with the backend API defined by the backend-agent.

## Development notes
- Install dependencies with `npm install`.
- Start the development server using `npm run dev`.
- The API base URL defaults to `http://localhost:8000` but can be overridden via `NEXT_PUBLIC_API_URL`.
- Keep components simple and avoid heavy UI frameworks.
- Before running Playwright tests, execute `npx playwright install` to download the required browser binaries. A helper script is available at `frontend/scripts/install_browsers.sh` and should be run from the `frontend` directory.
- Run browser tests using `npx playwright test`.

