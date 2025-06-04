# Project Roadmap

This document outlines potential enhancements to evolve the basic command-line
inventory tracker into a fully-fledged application with a front-end.

1. **Packaging and APIs**
   - Distribute the `stock` package on PyPI for reuse.
   - Provide a stable Python API for other applications.
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
