# Stock-Saas

A simple inventory tracker for a small department store room.

The project started as a CLI backed by a JSON file but now persists data in a
SQL database using SQLAlchemy. SQLite is used by default for local development
and you can point `DATABASE_URL` to a PostgreSQL database in production. Every
change to an item is written to an audit log table so history can be reviewed.
Administrators can export these logs as a CSV report via the API.

User accounts are stored in the same database. Authentication is handled with
JWT tokens and basic role based access control (admin, manager, user).
Credentials for the initial admin account are read from the environment
variables `ADMIN_USERNAME` and `ADMIN_PASSWORD`. When running with the default
SQLite database, missing values fall back to `admin`/`admin` for convenience.

Inventory data is scoped by **tenant**. Every item and user belongs to a tenant
record, identified by `tenant_id`. API requests must include this identifier so
the backend knows which tenant's inventory to operate on.

Recent updates include support for departments and categories, transferring
items between them, a registration endpoint with user management UI and
WebSocket notifications when stock levels drop.

## Features

- Multi-tenant inventory with role based access control
- Departments and categories to organise stock
- CSV export of audit logs and background tasks powered by Celery
- Async endpoints and database sessions using SQLAlchemy's async engine
- Analytics endpoints with optional Redis caching
- WebSocket notifications when stock is low
- Rate limiting for authentication and user management routes
- Password reset endpoints (`/auth/request-reset` and `/auth/reset-password`)
- Secrets can be loaded from an external JSON store
- Next.js frontend located in the `frontend/` directory

You can use the CLI or the API to manage inventory. When available stock falls
below a configured threshold, a warning is displayed during the status check.

## Quickstart


1. Copy `.env.example` to `.env` and adjust values. At a minimum set
   `SECRET_KEY`. `DATABASE_URL` defaults to SQLite but can be overridden.
   When running with `docker-compose` the backend container reads
  `SECRET_KEY` from this file. Optional settings include `ADMIN_USERNAME`,
  `ADMIN_PASSWORD`, `NEXT_PUBLIC_API_URL` for the frontend,
  `CORS_ALLOW_ORIGINS` for allowed CORS origins and background
  worker variables such as `CELERY_BROKER_URL`, `STOCK_CHECK_INTERVAL`,
  `REDIS_URL` for caching, `RATE_LIMIT_REDIS_URL` for the rate limiter,
  `ASYNC_DATABASE_URL` when using an async driver,
  `SLACK_WEBHOOK_URL`, `SMTP_SERVER`, `ALERT_EMAIL_TO` and
  `ALERT_EMAIL_FROM`. **Do not commit your `.env` file to version control as
  it may contain secrets.**
   When using `docker-compose`, set `NEXT_PUBLIC_API_URL` to
  `http://backend:8000` and `CORS_ALLOW_ORIGINS` to `http://localhost:3000`.
2. Install Python dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

3. Run the Celery worker to process stock alerts and CSV exports:

```bash
celery -A tasks worker -B
```

4. Open `http://localhost:8000/docs` and include `tenant_id` on every request
   to scope data to the correct tenant.

## Basic usage

```bash
# add 10 headphones with a low-stock threshold of 5
python inventory.py add headphones 10 --threshold 5

# issue 2 headphones to users
python inventory.py issue headphones 2

# return 1 headphone
python inventory.py return headphones 1

# view status of all items
python inventory.py status
```

Inventory data is stored in a SQLite database named `inventory.db` by default.
Set `DATABASE_URL` to use a different database engine. The application reads all
settings via `config.py` from environment variables defined in `.env`. Provide
`ADMIN_USERNAME` and `ADMIN_PASSWORD` to specify the first admin user's
credentials. The application looks for `SECRET_KEY` in the environment and will
fall back to the secret manager when `SECRET_STORE_FILE` is configured.


## Running the API

You can also manage inventory via a simple FastAPI service.

```bash
# install dependencies
pip install -r requirements.txt

# start the server
uvicorn main:app --reload
```

API endpoints mirror the CLI commands and are documented at `/docs` when the server is running.
Authenticate by posting your username and password to `/token` and include the returned token using `Authorization: Bearer <token>`.

### Required headers and parameters

All authenticated endpoints require an `Authorization` header with the JWT token
returned from `/token`. POST and PUT requests should also include
`Content-Type: application/json`.
Every API call must provide a `tenant_id` value (query parameter or JSON body)
to ensure the request is scoped to the correct tenant.

## Database migrations

Alembic manages schema changes. After installing dependencies you can
initialize the migration folder with:

```bash
alembic init alembic
```

When models are modified, create a new revision:

```bash
alembic revision --autogenerate -m "my change"
```

Apply migrations to the database defined by `DATABASE_URL`:

```bash
alembic upgrade head
```

## Testing

After installing the Python dependencies you can run the unit and API tests with `pytest`:

```bash
pip install -r requirements.txt
pytest
```

The `requirements.txt` file pins `httpx` to `0.27.*` to remain compatible with
`starlette==0.27.0`.

The tests use an in-memory SQLite database so they will not modify any local data files.

Browser tests live under `frontend/tests`. Install the Node dependencies and download
the Playwright browsers before running the test suite:

```bash
cd frontend
npm install
npx playwright install # or ./scripts/install_browsers.sh
npx playwright test
```

## External secret manager

When `SECRET_STORE_FILE` is defined, `config.py` loads `SECRET_KEY` from the
specified JSON file if the environment variable is missing. Rotate the key using
the helper script:

```bash
python scripts/rotate_secret.py --store path/to/secrets.json
```
### Example requests

Each item endpoint expects a JSON body matching the `ItemCreate` schema:

```json
{
  "name": "headphones",
  "quantity": 5,
  "threshold": 1
}
```

Issue and return operations ignore the `threshold` field but the same payload shape is used.

```bash
# add items
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"name":"headphones","quantity":10,"threshold":5,"tenant_id":1}' \
  http://localhost:8000/items/add

# issue items
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"name":"headphones","quantity":2,"tenant_id":1}' \
  http://localhost:8000/items/issue

# return items
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
-d '{"name":"headphones","quantity":1,"tenant_id":1}' \
  http://localhost:8000/items/return
```


### Audit log entries

Retrieve recent actions recorded in the audit log:

```bash
curl -H "Authorization: Bearer <token>" \
  'http://localhost:8000/audit/logs?limit=5'
```

You can also export the same data as CSV for reporting. The export runs in the
background so large reports do not block the request:

```bash
# start the export and note the returned task_id
curl -X POST -H "Authorization: Bearer <token>" \
  'http://localhost:8000/analytics/audit/export?limit=100'

# download the generated file using the task_id from above
curl -H "Authorization: Bearer <token>" \
  'http://localhost:8000/analytics/audit/export/<task_id>' -o audit_log.csv
```

## Running the Frontend

A simple Next.js interface lives in the `frontend/` folder. It uses the API server described above.
See [frontend/README.md](frontend/README.md) for a quickstart guide.

```bash
# install frontend dependencies
cd frontend && npm install

# start the development server
npm run dev
```

The frontend expects the FastAPI backend to run on `http://localhost:8000`. If your API is available elsewhere set the environment variable `NEXT_PUBLIC_API_URL` before starting the dev server.

The backend enables CORS using FastAPI's `CORSMiddleware`. When the
application runs with the default SQLite database (development mode), all
origins are allowed. In other environments the list of allowed origins is
read from the `CORS_ALLOW_ORIGINS` variable. If unset, it defaults to the value
of `NEXT_PUBLIC_API_URL`.

After logging in you will see the dashboard listing all items. Links are provided to pages for adding new stock, issuing items and recording returns. Each form uses the JWT token stored in `localStorage` to authenticate API requests.

Admins can also open `/users` to manage accounts. The page lists existing users and includes a form to create new ones.

The latest UI introduces a sidebar driven dashboard where stock is organised by **department** and **category**. Users can create, edit and delete departments or categories, restock items or transfer them between departments, and scan barcodes to look up stock quickly. A history dialog records all actions so past movements can be reviewed.

### Frontend tests

Playwright powers browser tests located in `frontend/tests`. Before running
`npx playwright test`, download the browser binaries:

```bash
cd frontend
npx playwright install
```

You can also run `./scripts/install_browsers.sh` inside `frontend/` to automate
this step.

## User registration

New users can sign up via the `/register` page in the Next.js frontend. The form
submits directly to the FastAPI endpoint `/auth/register`. When departments exist the page lets users choose one; otherwise
a tenant is created automatically. On success the user is redirected to the login
screen.

## Password reset

If a user forgets their password they can request a reset token by POSTing their
username to `/auth/request-reset`. The token returned from this endpoint should
be supplied to `/auth/reset-password` together with the new password. Tokens
expire after one hour.


## Running with Docker

A `Dockerfile` is provided to containerize the FastAPI service. Build and run it locally:

```bash
docker build -t stock-saas-backend .
docker run -e SECRET_KEY=mysecret -p 8000:8000 stock-saas-backend
```

To start the backend together with a PostgreSQL database and the Next.js frontend use `docker-compose`. The compose file loads environment variables from `.env`, so ensure `SECRET_KEY` is set there:

```bash
cp .env.example .env
# edit values as needed; docker-compose reads variables from this file
# When running the containers you should point the frontend at the
# backend service and allow requests from the browser:
# NEXT_PUBLIC_API_URL=http://backend:8000
# CORS_ALLOW_ORIGINS=http://localhost:3000
docker-compose up --build
```

Alternatively run `./scripts/quickstart.sh` to start all services.

The compose file also starts Redis along with Celery worker and beat containers
for background tasks. The API is available on `http://localhost:8000` and the
Next.js frontend on `http://localhost:3000` when the containers are running.



## Stock level notifications

A Celery beat task checks inventory every hour (configurable via `STOCK_CHECK_INTERVAL`) and sends alerts when available stock falls below the configured threshold. Alerts can be sent via Slack using `SLACK_WEBHOOK_URL` or via email using `SMTP_SERVER` and `ALERT_EMAIL_TO`. Each alert is recorded in the `notifications` table.

Users can choose whether they prefer email or Slack messages by setting the `notification_preference` field on their account. Notifications are delivered once per user based on this setting.
