import json

import redis

from app.core.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


def set_cache(
    key: str,
    value,
    expire: int = 300,
):
    redis_client.setex(
        key,
        expire,
        json.dumps(
            value,
            default=str
        ),
    )


def get_cache(key: str):
    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def delete_cache(key: str):
    redis_client.delete(key)


def clear_cache_pattern(pattern: str):
    keys = redis_client.keys(pattern)

    if keys:
        redis_client.delete(*keys)