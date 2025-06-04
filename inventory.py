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
    main()
