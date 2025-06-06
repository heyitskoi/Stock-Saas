# ops-agent Instructions

This file defines the **ops-agent** responsible for operational scripts and container configuration.

## Scope

These guidelines apply to the `scripts/` and `nginx/` directories.

## Responsibilities
- Build and maintain Docker images (`Dockerfile`).
- Use `docker-compose` to orchestrate services defined in `docker-compose.yml`.
- Manage the Nginx configuration at `nginx/default.conf`.
- Rotate secrets using `scripts/rotate_secret.py`.

## Quickstart

Run `scripts/quickstart.sh` from the project root to build and launch all containers with `docker-compose`.
