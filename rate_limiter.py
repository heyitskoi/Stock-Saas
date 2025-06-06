from typing import Iterable
import time
from collections import defaultdict

import redis.asyncio as redis

from fastapi import Request
from starlette.responses import JSONResponse


class RateLimiter:
    """Redis backed rate limiter."""

    def __init__(self, limit: int, window: int, routes: Iterable[str], redis_url: str):
        self.limit = limit
        self.window = window
        self.routes = list(routes)
        self.redis_url = redis_url
        self._memory_store = (
            defaultdict(list) if redis_url == "memory://" else None
        )

    async def __call__(self, request: Request, call_next):
        if any(request.url.path.startswith(route) for route in self.routes):
            key = f"rl:{request.client.host}:{request.url.path}"
            now = int(time.time())
            if self._memory_store is not None:
                queue = [t for t in self._memory_store[key] if t > now - self.window]
                if len(queue) >= self.limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests"},
                    )
                queue.append(now)
                self._memory_store[key] = queue
            else:
                async with redis.from_url(self.redis_url, decode_responses=True) as r:
                    await r.zremrangebyscore(key, 0, now - self.window)
                    count = await r.zcard(key)
                    if count >= self.limit:
                        return JSONResponse(
                            status_code=429,
                            content={"detail": "Too many requests"},
                        )
                    await r.zadd(key, {str(now): now})
                    await r.expire(key, self.window)
        response = await call_next(request)
        return response

    async def reset(self) -> None:
        if self._memory_store is not None:
            self._memory_store.clear()
        else:
            async with redis.from_url(self.redis_url, decode_responses=True) as r:
                keys = await r.keys("rl:*")
                if keys:
                    await r.delete(*keys)
