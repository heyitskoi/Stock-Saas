# Stock-Saas

A simple inventory tracker for a small department store room.

This project provides a command line tool `inventory.py` that stores data in
`inventory.json`. You can use it to add items, issue them to users, return
items, and check stock levels. When available stock falls below a configured
threshold, a warning is displayed during the status check.

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

Inventory data is stored locally in `inventory.json` in the project directory.

## Running the API

You can also manage inventory via a simple FastAPI service.

```bash
# install dependencies
pip install -r requirements.txt

# start the server
uvicorn main:app --reload
```

API endpoints mirror the CLI commands and are documented at `/docs` when the server is running.
