#updated Roadmap

🛣️ Project Roadmap
This roadmap tracks major milestones and workstreams for your inventory SaaS platform. It follows a modular agent-based structure.

✅ Completed
CLI-based inventory manager (inventory.py)

JSON file storage with threshold alerts

Ported CLI logic to FastAPI endpoints

Basic JWT authentication with role-based access control

Initial modular design and roadmap defined

🔄 In Progress / Next Priorities
🔧 Backend Agent
✅ Port CLI logic to FastAPI

✅ Add JWT auth and role-based access control

⚠️ Replace JSON with database (SQLite dev / PostgreSQL prod)

⏳ Implement audit logging for item changes

⏳ Add full user CRUD endpoints

🆕 Add CORS support for frontend integration

🆕 Clean up PEP8 style issues and apply formatting (black, flake8)

🆕 Add background task queue support for async ops (future-proofing)

🖥 Frontend Agent
✅ Bootstrap React/Next.js frontend with V0.dev

⏳ Build inventory dashboard and forms to consume API

🆕 Add user management UI (admin creating users, login)

🆕 Handle API auth tokens and session state properly

📊 Analytics Agent
⏳ Track item usage and change history (audit log visualization)

🆕 Export reports (CSV)

🆕 Add simple graphs or tables (e.g. most issued items, low stock)

🧪 Test Agent
⚠️ Fix failing tests (httpx/starlette version pinning)

⏳ Add unit tests for API routes and auth

⏳ Add integration tests for core flows (add/issue/return item)

🆕 Setup GitHub Actions for CI pipeline on push/PR

🆕 Add test data factory for easier test writing

🧭 Planned Future Work
🔐 Password reset, login throttling, 2FA

🧑‍💼 Multi-tenancy support (scoped data per company)

🔔 Notification system (e.g. low stock alerts)

🚀 Performance tuning and async optimizations

📦 Docker-based deployment with PostgreSQL and Nginx

📜 Admin audit trail export and report generation

Would you like this formatted as a markdown file (ROADMAP.md) to include in your repo directly?













# older Project Roadmap

This roadmap outlines completed work and upcoming tasks derived from the `checklist`.

## Completed
- Command line inventory manager (`inventory.py`)
- JSON file storage with threshold alerts
- Basic roadmap vision and modular design
- Initial FastAPI endpoints ported from CLI

## Next Steps
### Backend Agent (priority)
1. **DONE** Port CLI logic to FastAPI endpoints
2. Add user authentication (JWT) and role-based access control
3. Replace JSON with a database (SQLite in dev, PostgreSQL in prod)
4. Implement audit logging for item changes

### Frontend Agent
1. Begin React/Next.js interface using V0.dev components
2. Inventory dashboard and forms consuming backend APIs

### Analytics Agent
1. Track item usage history
2. Export reports (CSV) and basic dashboards

### Test Agent
1. Unit tests for API routes
2. Integration tests simulating common user flows

Further tasks like multi-tenancy, notifications, and performance tuning follow after the initial API rollout.
