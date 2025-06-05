# test-agent Instructions

This folder contains pytest suites driven by the **test-agent**.

## Responsibilities
- Validate the backend API and core logic.
- Simulate common user flows triggered by the frontend-agent.

## Running tests
- Install Python dependencies from `requirements.txt` and `pytest`.
- Execute all tests with `pytest` from the repository root.
- Tests rely on an in-memory SQLite database and will not affect local data files.

