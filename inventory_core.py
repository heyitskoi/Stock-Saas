import json
import os
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


def add_item(name: str, qty: int, threshold: int) -> dict:
    data = load_data()
    item = data.get(name, {"available": 0, "in_use": 0, "threshold": threshold})
    item["available"] += qty
    if threshold is not None:
        item["threshold"] = threshold
    data[name] = item
    save_data(data)
    return item


def issue_item(name: str, qty: int) -> dict:
    data = load_data()
    item = data.get(name)
    if not item or item["available"] < qty:
        raise ValueError("Not enough stock to issue")
    item["available"] -= qty
    item["in_use"] += qty
    save_data(data)
    return item


def return_item(name: str, qty: int) -> dict:
    data = load_data()
    item = data.get(name)
    if not item or item["in_use"] < qty:
        raise ValueError("Invalid return quantity")
    item["in_use"] -= qty
    item["available"] += qty
    save_data(data)
    return item


def get_status(name: str = None) -> Dict[str, dict]:
    data = load_data()
    if name:
        item = data.get(name)
        return {name: item} if item else {}
    return data
