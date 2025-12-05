import redis
from src.conf.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


class CachedObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
