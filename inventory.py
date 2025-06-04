
import argparse

from stock.inventory import Inventory


def print_table(rows: list[list[str]]) -> None:
    col_widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for row in rows:
        line = "  ".join(col.ljust(col_widths[i]) for i, col in enumerate(row))
        print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple inventory manager")
    subparsers = parser.add_subparsers(dest="command")

    add_p = subparsers.add_parser("add")
    add_p.add_argument("name")
    add_p.add_argument("quantity", type=int)
    add_p.add_argument("--threshold", type=int, default=None)

    issue_p = subparsers.add_parser("issue")
    issue_p.add_argument("name")
    issue_p.add_argument("quantity", type=int)

    return_p = subparsers.add_parser("return")
    return_p.add_argument("name")
    return_p.add_argument("quantity", type=int)

    status_p = subparsers.add_parser("status")
    status_p.add_argument("name", nargs="?")

    args = parser.parse_args()
    inv = Inventory()

    if args.command == "add":
        item = inv.add_item(args.name, args.quantity, args.threshold)
        print(f"Added {args.quantity} {args.name}(s). Available: {item['available']}")
    elif args.command == "issue":
        if not inv.issue_item(args.name, args.quantity):
            print("Not enough stock to issue")
        else:
            status = inv.get_status(args.name)[args.name]
            print(f"Issued {args.quantity} {args.name}(s). In use: {status['in_use']}")
    elif args.command == "return":
        if not inv.return_item(args.name, args.quantity):
            print("Invalid return quantity")
        else:
            status = inv.get_status(args.name)[args.name]
            print(f"Returned {args.quantity} {args.name}(s). Available: {status['available']}")
    elif args.command == "status":
        table = inv.get_status_table(args.name)
        if len(table) == 1:
            print("No items found")
            return
        print_table(table)
        for row in table[1:]:
            if int(row[1]) < int(row[3]):
                print(f"WARNING: {row[0]} stock below threshold")
    else:
        parser.print_help()


if __name__ == "__main__":
=======
import json
import os
import argparse
from typing import Dict

DATA_FILE = 'inventory.json'

def load_data() -> Dict[str, dict]:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data: Dict[str, dict]):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_item(name: str, qty: int, threshold: int):
    data = load_data()
    item = data.get(name, {"available": 0, "in_use": 0, "threshold": threshold})
    item['available'] += qty
    if 'threshold' not in item or threshold is not None:
        item['threshold'] = threshold
    data[name] = item
    save_data(data)
    print(f"Added {qty} {name}(s). Available: {item['available']}")


def issue_item(name: str, qty: int):
    data = load_data()
    item = data.get(name)
    if not item or item['available'] < qty:
        print('Not enough stock to issue')
        return
    item['available'] -= qty
    item['in_use'] += qty
    save_data(data)
    print(f"Issued {qty} {name}(s). In use: {item['in_use']}")


def return_item(name: str, qty: int):
    data = load_data()
    item = data.get(name)
    if not item or item['in_use'] < qty:
        print('Invalid return quantity')
        return
    item['in_use'] -= qty
    item['available'] += qty
    save_data(data)
    print(f"Returned {qty} {name}(s). Available: {item['available']}")


def status(name: str = None):
    data = load_data()
    if name:
        items = {name: data.get(name)} if name in data else {}
    else:
        items = data
    if not items:
        print('No items found')
        return
    for k, item in items.items():
        available = item['available']
        in_use = item['in_use']
        threshold = item.get('threshold', 0)
        print(f"{k}: available={available}, in_use={in_use}, threshold={threshold}")
        if available < threshold:
            print(f"  WARNING: {k} stock below threshold")


def main():
    parser = argparse.ArgumentParser(description='Simple inventory manager')
    subparsers = parser.add_subparsers(dest='command')

    add_p = subparsers.add_parser('add')
    add_p.add_argument('name')
    add_p.add_argument('quantity', type=int)
    add_p.add_argument('--threshold', type=int, default=None)

    issue_p = subparsers.add_parser('issue')
    issue_p.add_argument('name')
    issue_p.add_argument('quantity', type=int)

    return_p = subparsers.add_parser('return')
    return_p.add_argument('name')
    return_p.add_argument('quantity', type=int)

    status_p = subparsers.add_parser('status')
    status_p.add_argument('name', nargs='?')

    args = parser.parse_args()

    if args.command == 'add':
        add_item(args.name, args.quantity, args.threshold or 0)
    elif args.command == 'issue':
        issue_item(args.name, args.quantity)
    elif args.command == 'return':
        return_item(args.name, args.quantity)
    elif args.command == 'status':
        status(args.name)
    else:
        parser.print_help()

if __name__ == '__main__':

    main()
