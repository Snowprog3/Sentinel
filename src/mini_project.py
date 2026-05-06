import asyncio
import time

import httpx

from error_handler import handle_exception
from proxy import proxy
from urls import TEST_URLS
from utils import build_filename_from_url, ensure_dir

proxy()


async def download_one(
    client: httpx.AsyncClient, url: str, output_dir: str = "data/raw"
) -> tuple[str, bool]:  # noqa
    """Download page and return (raw_page, True/False)"""
    save_path = build_filename_from_url(url, output_dir)
    try:
        ensure_dir(save_path)
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        save_path.write_text(response.text, encoding="utf-8")
        print(f"[OK] {url} - {save_path}")
        return url, True
    except (httpx.HTTPStatusError, httpx.RequestError, httpx.ReadTimeout) as e:
        handle_exception(e)
        print(f"[FAIL] {url}")
        return url, False


async def main() -> None:
    print(f"Begin to launch {len(TEST_URLS)} pages ...")
    start = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [download_one(client, url) for url in TEST_URLS]
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    success_count = sum(1 for _, ok in results if ok)
    failed_count = len(results) - success_count

    print(f"Task ending for {elapsed:.2f} seconds")
    print(f"Success - {success_count}, failed - {failed_count}")


if __name__ == "__main__":
    asyncio.run(main())
