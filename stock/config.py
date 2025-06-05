"""Configuration loading for inventory system."""

import json
import os
from typing import Any, Dict

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

_defaults: Dict[str, Any] = {
    "default_threshold": 1,
    "data_file": os.path.join(os.path.dirname(os.path.dirname(__file__)), "inventory.json"),
}


def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE):
        return _defaults.copy()
    with open(CONFIG_FILE, "r") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError:
            return _defaults.copy()
    return {**_defaults, **cfg}
