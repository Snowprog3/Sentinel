import httpx
from pathlib import Path

def download_page(url: str, save_path: Path) -> None:
    """Parsing of the probe page"""
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        """Error on the server"""
        print(f"Error HTTP: {e.response.status_code}")
    except httpx.RequestError as e:
        """Network error"""
        print(f"Network error: {e}")

    """Not errors and save date into file"""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(response.text, encoding="utf-8")
    print(f"Save: {save_path}")
    print(f"Status: {response.status_code}")
    print(f"Content-type: {response.headers.get('content-type')}")


if __name__ == "__main__":
    download_page("http://books.toscrape.com", Path("data/raw/books_main.html"))