# Project Roadmap

This document highlights major milestones for the inventory SaaS platform.

## Completed
- CLI-based inventory manager
- Database storage using SQLite or PostgreSQL via SQLAlchemy
- FastAPI API with JWT authentication and role based access
- Audit logging with CSV export
- Multi-tenant data separation
- Departments, categories and item transfer
- User registration and management UI
- React/Next.js frontend dashboard and forms
- Background tasks with Celery and WebSocket notifications
- GitHub Actions CI and Docker/Nginx deployment
- Password reset endpoints and user self-service
- Rate limiting to protect authentication routes
- Redis caching for analytics endpoints

## In Progress
- Expanded analytics dashboards with usage trends
- Continuous integration of Playwright and Pytest suites
- Helper scripts for local Docker workflows

## Planned
- Two-factor authentication support
- Further async optimisations for heavy workloads
- Additional notification options (email/Slack)
