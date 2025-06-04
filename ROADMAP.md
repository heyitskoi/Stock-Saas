# Project Roadmap

This roadmap outlines completed work and upcoming tasks derived from the `checklist`.

## Completed
- Command line inventory manager (`inventory.py`)
- JSON file storage with threshold alerts
- Basic roadmap vision and modular design

## Next Steps
### Backend Agent (priority)
1. Port CLI logic to FastAPI endpoints
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
