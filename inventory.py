import argparse

from stock.inventory import Inventory


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
        items = inv.get_status(args.name)
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
