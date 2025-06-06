from functools import lru_cache
import json
from typing import Any, List

import redis

from config import settings


@lru_cache()
def get_redis() -> redis.Redis | None:
    try:
        return redis.Redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        return None


def get_cached(key: str) -> List[dict] | None:
    client = get_redis()
    if not client:
        return None
    try:
        value = client.get(key)
        if value is not None:
            return json.loads(value)
    except Exception:
        return None
    return None


def set_cached(key: str, value: List[dict], ttl: int) -> None:
    client = get_redis()
    if not client:
        return
    try:
        client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass
