from typing import Iterable
import time

from fastapi import Request
from starlette.responses import JSONResponse


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, limit: int, window: int, routes: Iterable[str]):
        self.limit = limit
        self.window = window
        self.routes = list(routes)
        self.attempts: dict[tuple[str, str], list[float]] = {}

    async def __call__(self, request: Request, call_next):
        if any(request.url.path.startswith(route) for route in self.routes):
            key = (request.client.host, request.url.path)
            now = time.time()
            timestamps = [
                t for t in self.attempts.get(key, []) if now - t < self.window
            ]
            if len(timestamps) >= self.limit:
                return JSONResponse(
                    status_code=429, content={"detail": "Too many requests"}
                )
            timestamps.append(now)
            self.attempts[key] = timestamps
        response = await call_next(request)
        return response

    def reset(self) -> None:
        self.attempts.clear()
