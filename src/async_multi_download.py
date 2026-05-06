import asyncio
import os
import time
from pathlib import Path

import httpx

from error_handler import handle_exception

for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
    os.environ.pop(var, None)


async def download_one(client: httpx.AsyncClient, url: str, save_path: Path) -> None:
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(response.text, encoding="utf-8")
        print(f"[OK] {url} -> {save_path} (status: {response.status_code})")
    except httpx.HTTPStatusError as e:
        handle_exception(e)
        return
    except httpx.ReadTimeout:
        print(f"[TIMEOUT] {url} -> сервер не ответил за 10 секунд")
    except httpx.RequestError as e:
        handle_exception(e)
        return


async def main() -> None:
    urls = [
        "http://books.toscrape.com",
        "http://httpbin.com/get",
        "http://books.toscrape.com/catalogue/page-2.html",
    ]

    output_dir = Path("data/raw")

    start = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [
            download_one(client, url, output_dir / f"{url.split('/')[-1] or 'index'}.html")
            for url in urls
        ]
        await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"\nelapsed time is {elapsed:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
