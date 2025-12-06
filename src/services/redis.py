"""Redis client and helper class for caching objects."""

import redis
from src.conf.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)
"""Global Redis client used for caching user data."""


class CachedObject:
    """Simple helper that turns a dict into an object with attributes."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
