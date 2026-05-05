import os
from pathlib import Path

import httpx
import pytest
import respx

from src.async_multi_download import download_one


def test_respx_basic():
    # Удаляем прокси-переменные
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
        os.environ.pop(var, None)
    url = "http://test.com"
    with respx.mock:
        respx.get(url).respond(status_code=200, text="Hello, world")
        response = httpx.get(url)
        assert response.status_code == 200
        assert response.text == "Hello, world"


@pytest.mark.asyncio
async def test_download_one_success(tmp_path: Path):
    url = "http://test.com/asyncio"
    save_path = tmp_path / "output.html"
    async with httpx.AsyncClient() as client:
        with respx.mock:
            respx.get(url).respond(status_code=200, text="async test")
            await download_one(client, url, save_path)

    assert save_path.exists()
    assert save_path.read_text() == "async test"


@pytest.mark.asyncio
async def test_download_one_http_error(tmp_path: Path, capsys):
    url = "http://test.com/async_error"
    save_path = tmp_path / "output.html"
    async with httpx.AsyncClient() as client:
        with respx.mock:
            respx.get(url).respond(status_code=500)
            await download_one(client, url, save_path)

    assert not save_path.exists()
    captured = capsys.readouterr()
    assert "Error HTTP: 500" in captured.out
