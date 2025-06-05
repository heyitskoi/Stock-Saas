# Project Roadmap

This document outlines potential enhancements to evolve the basic command-line
inventory tracker into a fully-fledged application with a front-end.

1. **Packaging and APIs**
   - ✅ Organize code as a reusable `stock` package.
   - Distribute the package on PyPI for reuse.
   - Provide a stable Python API for other applications.
   - ✅ Load configuration from `config.json`.
   - ✅ Basic logging of inventory operations.
   - ✅ Validation to prevent negative stock levels.
2. **Web Interface**
   - Build a simple web UI using Flask or FastAPI.
   - Add authentication so different departments can manage their own stock.
   - Expose REST endpoints for integration with other tools.
3. **Notifications**
   - Allow configuring email or chat notifications when items fall below
     threshold levels.
   - Schedule periodic reminders about low stock.
4. **Reporting and Analytics**
   - Generate usage reports (e.g. most issued items, historical trends).
   - Export data to CSV for further analysis.
5. **Data management**
   - Support multiple stores/locations with a relational database backend.
   - Provide import/export utilities for bulk item updates.
6. **User roles and permissions**
   - Define roles such as admin, manager and regular user.
   - Restrict certain actions (like disposal) to authorized roles.

This list is a starting point and can be expanded as requirements grow.
=======
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
