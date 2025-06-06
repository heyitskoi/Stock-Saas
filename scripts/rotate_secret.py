#!/usr/bin/env python
"""Rotate SECRET_KEY stored in the configured secret manager."""

import argparse
import os
import secrets

from secrets_manager import get_manager


def main() -> None:
    parser = argparse.ArgumentParser(description="Rotate SECRET_KEY")
    parser.add_argument(
        "--store",
        default=os.environ.get("SECRET_STORE_FILE"),
        help="Path to the secret store file",
    )
    args = parser.parse_args()

    manager = get_manager(args.store)
    if not manager:
        raise SystemExit("No secret store configured")

    new_key = secrets.token_urlsafe(32)
    manager.set_secret("SECRET_KEY", new_key)
    print("SECRET_KEY rotated")


if __name__ == "__main__":
    main()
