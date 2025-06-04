# Stock-Saas

A simple inventory tracker for a small department store room. The code is
organized as a package so it can later be reused from a web or desktop
front‑end.

The command line entry point is `inventory.py` which stores data in
`inventory.json` (configurable via `config.json`). You can use it to add
items, issue them to users, return items and check stock levels. When available
stock falls below a configured threshold, a warning is displayed during the
status check.

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

Configuration options can be adjusted in `config.json`. The default file
contains the path to `inventory.json` and a `default_threshold` used when
adding items without specifying one.

Inventory data is stored locally using the path defined in `config.json`.

## Development roadmap

See [ROADMAP.md](ROADMAP.md) for a high-level plan of upcoming features.

Run the unit tests with:

```bash
python -m pytest
```
