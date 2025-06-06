import importlib

try:
    BaseSettings = getattr(importlib.import_module("pydantic_settings"), "BaseSettings")
except Exception:  # fallback to bundled stub for pydantic v1
    from pydantic import BaseSettings  # type: ignore

__all__ = ["BaseSettings"]
