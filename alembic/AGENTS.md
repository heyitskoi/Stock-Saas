# db-agent Instructions

This folder contains Alembic migration scripts used to evolve the database schema.
It is maintained by the **db-agent** (also referred to as the **backend-agent**).

## Generating migrations
- After changing SQLAlchemy models, create a new revision with
  ```bash
  alembic revision --autogenerate -m "describe change"
  ```
  This command inspects the models and database to produce a migration file
  under `alembic/versions`.

## Applying migrations
- Apply all outstanding migrations to the configured database using
  ```bash
  alembic upgrade head
  ```
Run this whenever the application starts on a new environment or when
deploying updates. The `scripts/quickstart.sh` helper runs this automatically
for Docker deployments.
