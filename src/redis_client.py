import redis.asyncio as aioredis

from src.config import settings

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"


async def is_url_processed(url: str) -> bool:
    """Check processing of url"""
    async with aioredis.from_url(REDIS_URL) as client:
        was_set = await client.set(url, "1", nx=True, ex=86400)
        return not was_set


async def mark_url_processed(url: str) -> None:
    """url = processed"""
    async with aioredis.from_url(REDIS_URL) as client:
        await client.set(url, "1", ex=86400)
