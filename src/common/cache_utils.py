import json
from typing import Callable, Awaitable, Any
from src.core.redis_client import redis_client  


async def get_or_set_cache(
    key: str,
    expire: int,
    fetch_func: Callable[[], Awaitable[Any]]
) -> Any:
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    result = await fetch_func()
    await redis_client.set(key, json.dumps(result, default=str), ex=expire)
    return result
