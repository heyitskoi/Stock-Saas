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

You can use the CLI or the API to manage inventory. When available stock falls
below a configured threshold, a warning is displayed during the status check.

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
Set `DATABASE_URL` to use a different database engine. You can also provide
`ADMIN_USERNAME` and `ADMIN_PASSWORD` to specify the first admin user's
credentials. The API also expects a `SECRET_KEY` environment variable used to
sign JWT tokens.


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

## Running tests

After installing the project dependencies you can run the unit and API tests with `pytest`:

```bash
pip install -r requirements.txt
pip install pytest
pytest
```

The `requirements.txt` file pins `httpx` to `0.27.*` to remain compatible with
`starlette==0.27.0`.

The tests use an in-memory SQLite database so they will not modify any local data files.
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
  -d '{"name":"headphones","quantity":10,"threshold":5}' http://localhost:8000/items/add

# issue items
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"name":"headphones","quantity":2}' http://localhost:8000/items/issue

# return items
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
-d '{"name":"headphones","quantity":1}' http://localhost:8000/items/return
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

```bash
# install frontend dependencies
cd frontend && npm install

# start the development server
npm run dev
```

By default it expects the FastAPI backend to run on `http://localhost:8000`. You can change this by setting `NEXT_PUBLIC_API_URL` when starting the Next.js server.

The backend now enables CORS using FastAPI's `CORSMiddleware`. When the
application runs with the default SQLite database (development mode), all
origins are allowed. In other environments requests are only accepted from the
origin specified in `NEXT_PUBLIC_API_URL`.

After logging in you will see the dashboard listing all items. Links are provided to pages for adding new stock, issuing items and recording returns. Each form uses the JWT token stored in `localStorage` to authenticate API requests.

Admins can also open `/users` to manage accounts. The page lists existing users and includes a form to create new ones.



## Running with Docker

A `Dockerfile` is provided to containerize the FastAPI service. Build and run it locally:

```bash
docker build -t stock-saas-backend .
docker run -e SECRET_KEY=mysecret -p 8000:8000 stock-saas-backend
```

To start the backend together with a PostgreSQL database and the Next.js frontend use `docker-compose`:

```bash
docker-compose up --build
```

The API will be available on `http://localhost:8000` and the frontend on `http://localhost:3000`.


