import json
import os
from typing import Dict

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inventory.json')


def load_data() -> Dict[str, dict]:
    """Load inventory data from DATA_FILE."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data: Dict[str, dict]):
    """Persist inventory data to DATA_FILE."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
