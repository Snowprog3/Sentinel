import asyncio
import time
from pathlib import Path

import httpx


async def download_one(client: httpx.AsyncClient, url: str, save_path: Path) -> None:
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(response.text, encoding="utf-8")
        print(f"[OK] {url} -> {save_path} (status: {response.status_code})")
    except httpx.HTTPStatusError as e:
        print(f"HTTPError {url}: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"NetworkError {url}: {e}")


async def main() -> None:
    urls = [
        "http://books.toscrape.com",
        "http://httpbin.org/get",
        "http://books.toscrape.com/catalogue/page-2.html",
    ]

    output_dir = Path("data/raw")

    start = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [
            download_one(client, url, output_dir / f"{url.split('/')[-1] or 'index'} .html")
            for url in urls
        ]
        await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"\nelapsed time is {elapsed:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
