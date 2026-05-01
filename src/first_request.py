from pathlib import Path

import httpx

from error_handler import handle_exception


def download_page(url: str, save_path: Path) -> None:
    """Parsing of the probe page"""
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        handle_exception(e)
        return
    except httpx.RequestError as e:
        handle_exception(e)
        return

    """Not errors and save date into file"""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(response.text, encoding="utf-8")
    print(f"Save: {save_path}")
    print(f"Status: {response.status_code}")
    print(f"Content-type: {response.headers.get('content-type')}")


if __name__ == "__main__":
    download_page("http://books.toscrape.com", Path("data/raw/books_main.html"))
