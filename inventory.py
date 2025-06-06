import argparse

from inventory_core import (
    add_item as core_add_item,
    issue_item as core_issue_item,
    return_item as core_return_item,
    get_status,
)
from database import SessionLocal, engine
from models import Base

Base.metadata.create_all(bind=engine)


def add_item(db, name: str, qty: int, threshold: int, tenant_id: int):
    item = core_add_item(db, name, qty, threshold, tenant_id)
    print(f"Added {qty} {name}(s). Available: {item.available}")


def issue_item(db, name: str, qty: int, tenant_id: int):
    try:
        item = core_issue_item(db, name, qty, tenant_id)
        print(f"Issued {qty} {name}(s). In use: {item.in_use}")
    except ValueError:
        print("Not enough stock to issue")


def return_item(db, name: str, qty: int, tenant_id: int):
    try:
        item = core_return_item(db, name, qty, tenant_id)
        print(f"Returned {qty} {name}(s). Available: {item.available}")
    except ValueError:
        print("Invalid return quantity")


def status(db, tenant_id: int, name: str = None):
    items = get_status(db, tenant_id, name)
    if not items:
        print("No items found")
        return

    for k, item in items.items():
        available = item["available"]
        in_use = item["in_use"]
        threshold = item.get("threshold", 0)
        print(f"{k}: available={available}, in_use={in_use}, threshold={threshold}")
        if available < threshold:
            print(f"  WARNING: {k} stock below threshold")


def main():
    parser = argparse.ArgumentParser(description="Simple inventory manager")
    parser.add_argument("--tenant", type=int, default=1)
    subparsers = parser.add_subparsers(dest="command")

    add_p = subparsers.add_parser("add")
    add_p.add_argument("name")
    add_p.add_argument("quantity", type=int)
    add_p.add_argument("--threshold", type=int, default=0)

    issue_p = subparsers.add_parser("issue")
    issue_p.add_argument("name")
    issue_p.add_argument("quantity", type=int)

    return_p = subparsers.add_parser("return")
    return_p.add_argument("name")
    return_p.add_argument("quantity", type=int)

    status_p = subparsers.add_parser("status")
    status_p.add_argument("name", nargs="?")

    args = parser.parse_args()

    db = SessionLocal()
    try:
        tenant_id = args.tenant

        if args.command == "add":
            add_item(db, args.name, args.quantity, args.threshold, tenant_id)
        elif args.command == "issue":
            issue_item(db, args.name, args.quantity, tenant_id)
        elif args.command == "return":
            return_item(db, args.name, args.quantity, tenant_id)
        elif args.command == "status":
            status(db, tenant_id, args.name)
        else:
            parser.print_help()
    finally:
        db.close()


if __name__ == "__main__":
    main()
