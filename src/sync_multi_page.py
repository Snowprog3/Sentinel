import os
import time
from pathlib import Path

import httpx

for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
    os.environ.pop(var, None)


def download_one(url: str, client: httpx.Client, save_path: Path) -> Path:
    try:
        response = client.get(url, timeout=10.0)
        response.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(response.text, encoding="utf-8")
        print(f"Save text from {url} into {save_path}")
    except httpx.HTTPStatusError as e:
        print(f"HTTPError is {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"Network Error is {e}")


def main() -> None:
    urls = [
        "http://books.toscrape.com",
        "http://httpbin.org/get",
        "http://books.toscrape.com/catalogue/page-2.html",
    ]

    output_dir = Path("data/raw")

    start = time.time()

    with httpx.Client(proxy=None) as client:
        for url in urls:
            download_one(url, client, output_dir / f"{url.split('/')[-1] or 'index'}.html")

    elapsed = time.time() - start

    print(f"Elapsed {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
