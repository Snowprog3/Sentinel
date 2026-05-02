import os
from pathlib import Path

import httpx
import pytest
import respx

from src.async_multi_download import download_one
from src.first_request import download_page


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


def test_download_page_success(tmp_path: Path):
    url = "http://test.com"
    save_path = tmp_path / "output.html"
    with respx.mock:
        respx.get(url).respond(status_code=200, text="<html>test</html>")
        download_page(url, save_path)

    assert save_path.exists()
    assert save_path.read_text() == "<html>test</html>"


def test_download_page_http_error(tmp_path: Path, capsys):
    """Test of error 404"""
    url = "http://test.com/notfound"
    save_path = tmp_path / "output.html"
    with respx.mock:
        respx.get(url).respond(status_code=404)
        download_page(url, save_path)
    # File dont create
    assert not save_path.exists()
    # Check are the message about the error
    captured = capsys.readouterr()
    assert "Error HTTP: 404" in captured.out


def test_download_page_nerwork_error(tmp_path: Path, capsys):
    """Test of nerwork error"""
    url = "http://test.com/connect"
    save_path = tmp_path / "output.html"
    with respx.mock:
        respx.get(url).mock(side_effect=httpx.ConnectError("connection failed"))
        download_page(url, save_path)

    assert not save_path.exists()
    captured = capsys.readouterr()
    assert "ConnectError" in captured.out or "connection failed" in captured.out


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
