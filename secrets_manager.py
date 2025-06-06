import json
import os
from typing import Optional


class FileSecretsManager:
    """Simple file-based secret manager used for development/testing."""

    def __init__(self, path: str) -> None:
        self.path = path
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({}, fh)

    def _load(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def get_secret(self, name: str) -> Optional[str]:
        return self._load().get(name)

    def set_secret(self, name: str, value: str) -> None:
        data = self._load()
        data[name] = value
        self._save(data)


def get_manager(path: Optional[str]) -> Optional[FileSecretsManager]:
    if not path:
        return None
    return FileSecretsManager(path)
