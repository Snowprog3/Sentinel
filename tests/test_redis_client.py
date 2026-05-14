import pytest
import redis.asyncio as aioredis

from src.redis_client import is_url_processed


@pytest.mark.asyncio
async def test_duplicate_detection():
    url = "http://test.com/redis-test"
    # Убедимся, что ключа нет
    async with aioredis.from_url("redis://localhost:6379") as client:
        await client.delete(url)

    assert not await is_url_processed(url)  # ключа ещё нет → False (не обработан)
    # После первого вызова ключ появился
    assert await is_url_processed(url)  # теперь True
