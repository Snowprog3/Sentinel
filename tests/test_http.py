from pathlib import Path

import httpx
import pytest
import respx

from src.mini_project import download_one
from src.proxy import proxy
from src.utils import build_filename_from_url


def test_respx_basic():
    # Удаляем прокси-переменные
    proxy()
    url = "http://test.com"
    with respx.mock:
        respx.get(url).respond(status_code=200, text="Hello, world")
        response = httpx.get(url)
        assert response.status_code == 200
        assert response.text == "Hello, world"


@pytest.mark.asyncio
async def test_download_one_success(tmp_path: Path):
    url = "http://test.com/asyncio"
    async with httpx.AsyncClient() as client:
        with respx.mock:
            respx.get(url).respond(status_code=200, text="async test")
            await download_one(client, url, str(tmp_path))

    expected_name = build_filename_from_url(url, str(tmp_path)).name
    saved_file = tmp_path / expected_name
    assert saved_file.exists()
    assert saved_file.read_text() == "async test"


@pytest.mark.asyncio
async def test_download_one_http_error(tmp_path: Path, capsys):
    url = "http://test.com/async_error"
    save_path = tmp_path / "output.html"
    async with httpx.AsyncClient() as client:
        with respx.mock:
            respx.get(url).respond(status_code=500)
            await download_one(client, url, str(save_path))

    expected_name = build_filename_from_url(url, str(tmp_path)).name
    saved_file = tmp_path / expected_name
    assert not saved_file.exists()
    captured = capsys.readouterr()
    assert "Error HTTP: 500" in captured.out
