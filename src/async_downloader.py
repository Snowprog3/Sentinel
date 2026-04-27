"""First async downloader"""

import asyncio
from pathlib import Path

import httpx


async def download_page(url: str, save_path: Path) -> None:
    """Async downloading page and save her to the file"""
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        res.raise_for_status
        save_path.write_bytes(res.content)
        print(f"Save {save_path}: length: {len(res.content)} bytes")


async def main() -> None:
    """Use"""
    url = "https://books.toscrape.com"
    output = Path("downloaded_page.html")
    await download_page(url, output)


if __name__ == "__main__":
    asyncio.run(main())
