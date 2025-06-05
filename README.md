# Stock-Saas

A simple inventory tracker for a small department store room.

The project started as a CLI backed by a JSON file but now persists data in a
SQL database using SQLAlchemy. SQLite is used by default for local development
and you can point `DATABASE_URL` to a PostgreSQL database in production. Every
change to an item is written to an audit log table so history can be reviewed.

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
credentials.
=======
Set `DATABASE_URL` to use a different database engine. The API also expects a
`SECRET_KEY` environment variable used to sign JWT tokens.


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
=======
## Running the Frontend

A simple Next.js interface lives in the `frontend/` folder. It uses the API server described above.

```bash
# install frontend dependencies
cd frontend && npm install

# start the development server
npm run dev
```

By default it expects the FastAPI backend to run on `http://localhost:8000`. You can change this by setting `NEXT_PUBLIC_API_URL` when starting the Next.js server.

