from typing import Dict
import logging

from .config import load_config

from . import storage


class Inventory:
    """Core inventory operations."""

    def __init__(self):
        self.config = load_config()
        self._data = storage.load_data()
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    def _persist(self):
        storage.save_data(self._data)

    def add_item(self, name: str, qty: int, threshold: int | None = None):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        if threshold is None:
            threshold = self.config.get("default_threshold", 1)
        item = self._data.get(name, {"available": 0, "in_use": 0, "threshold": threshold})
        item["available"] += qty
        item["threshold"] = threshold if threshold is not None else item.get("threshold", 0)
        self._data[name] = item
        logging.info("Added %s x%d (threshold %d)", name, qty, threshold)
        self._persist()
        return item

    def issue_item(self, name: str, qty: int) -> bool:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        item = self._data.get(name)
        if not item or item["available"] < qty:
            return False
        item["available"] -= qty
        item["in_use"] += qty
        logging.info("Issued %s x%d", name, qty)
        self._persist()
        return True

    def return_item(self, name: str, qty: int) -> bool:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        item = self._data.get(name)
        if not item or item["in_use"] < qty:
            return False
        item["in_use"] -= qty
        item["available"] += qty
        logging.info("Returned %s x%d", name, qty)
        self._persist()
        return True

    def get_status(self, name: str | None = None) -> Dict[str, dict]:
        if name:
            return {name: self._data.get(name)} if name in self._data else {}
        return self._data

    def get_status_table(self, name: str | None = None) -> list[list[str]]:
        items = self.get_status(name)
        table = [["Item", "Available", "In Use", "Threshold"]]
        for k, item in items.items():
            table.append([
                k,
                str(item["available"]),
                str(item["in_use"]),
                str(item.get("threshold", 0)),
            ])
        return table
