"""
This is the entry point for a multi-tenant SaaS Stock Management platform built with FastAPI.

Main modules:
- auth (JWT-based login, register)
- products (CRUD, company-specific)
- stock (warehouse tracking, transfers)
- audit_log (logs every action)
- RBAC enforced via user roles
"""

# Set up FastAPI app with middleware, exception handlers, and route includes
