import asyncio

import pytest
import redis.asyncio as aioredis

from src.redis_client import is_url_processed

REDIS_TEST_URL = "redis://localhost:6379"


@pytest.mark.asyncio
async def test_duplicate_detection():
    url = "http://test.com/redis-test"
    # Убедимся, что ключа нет
    async with aioredis.from_url("redis://localhost:6379") as client:
        await client.delete(url)

    assert not await is_url_processed(url)  # ключа ещё нет → False (не обработан)
    # После первого вызова ключ появился
    assert await is_url_processed(url)  # теперь True


@pytest.mark.asyncio
async def test_first_call_returns_false():
    url = "http://books.toscrape.com/redis-test-1"
    async with aioredis.from_url(REDIS_TEST_URL) as client:
        await client.delete(url)  # чистим перед тестом
    result = await is_url_processed(url)
    assert result is False  # первый раз – не обработан


@pytest.mark.asyncio
async def test_second_call_returns_true():
    url = "http://books.toscrape.com/redis-test-2"
    async with aioredis.from_url(REDIS_TEST_URL) as client:
        await client.delete(url)
    first = await is_url_processed(url)
    second = await is_url_processed(url)
    assert first is False
    assert second is True


@pytest.mark.asyncio
async def test_after_key_expiry():
    url = "http://books.toscrape.com/redis-test-3"
    async with aioredis.from_url(REDIS_TEST_URL) as client:
        await client.delete(url)
        await client.set(url, "1", ex=1)  # TTL 1 секунда
        assert await is_url_processed(url) is True
        await asyncio.sleep(1.5)
        assert await is_url_processed(url) is False
