from typing import Dict

from . import storage


class Inventory:
    """Core inventory operations."""

    def __init__(self):
        self._data = storage.load_data()

    def _persist(self):
        storage.save_data(self._data)

    def add_item(self, name: str, qty: int, threshold: int | None = None):
        item = self._data.get(name, {"available": 0, "in_use": 0, "threshold": threshold or 0})
        item["available"] += qty
        if threshold is not None or "threshold" not in item:
            item["threshold"] = threshold or 0
        self._data[name] = item
        self._persist()
        return item

    def issue_item(self, name: str, qty: int) -> bool:
        item = self._data.get(name)
        if not item or item["available"] < qty:
            return False
        item["available"] -= qty
        item["in_use"] += qty
        self._persist()
        return True

    def return_item(self, name: str, qty: int) -> bool:
        item = self._data.get(name)
        if not item or item["in_use"] < qty:
            return False
        item["in_use"] -= qty
        item["available"] += qty
        self._persist()
        return True

    def get_status(self, name: str | None = None) -> Dict[str, dict]:
        if name:
            return {name: self._data.get(name)} if name in self._data else {}
        return self._data
