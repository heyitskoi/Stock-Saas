# SaaS Stock Management Platform

This is a multi-tenant stock management system using FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

## Features
- JWT Authentication and Role-Based Access Control (RBAC)
- Multi-tenancy: All models are scoped by `company_id`
- Products: SKU, quantity, price, and company-specific stock
- Internal and sellable stock modules
- Warehouses and stock transfers
- Audit logging of every create/update/delete
- Modular structure (models, schemas, routes, services)
