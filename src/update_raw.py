import asyncio
import logging

import httpx
from sqlalchemy import select, update

from src.artifact_saver import upload_raw_html
from src.database import engine
from src.models import Book
from src.proxy import proxy

proxy()

logger = logging.getLogger(__name__)


async def update_raw_data() -> None:
    """Скачивает страницы для книг, у которых отсутствует HTML в raw_data,
    сохраняет HTML в MinIO и обновляет raw_data и raw_data_key в БД.
    """
    # 1. Собираем идентификаторы и URL нужных книг
    async with engine.begin() as conn:
        stmt = select(Book.id, Book.url).where(
            Book.raw_data.is_(None) | (not Book.raw_data.has_key("html"))
        )
        result = await conn.execute(stmt)
        books = result.all()

    if not books:
        logger.info("Все книги уже содержат HTML в raw_data.")
        return

    # 2. Для каждой книги делаем запрос и обновляем БД
    async with httpx.AsyncClient(timeout=15) as client:
        for book_id, book_url in books:
            try:
                response = await client.get(book_url)
                response.raise_for_status()
                html = response.text

                # Загружаем HTML в MinIO и получаем ключ
                key = upload_raw_html(
                    book_id,
                    html,
                    {"url": book_url, "source": "update_raw_script"},
                )

                # Обновляем raw_data и raw_data_key в БД
                async with engine.begin() as conn:
                    await conn.execute(
                        update(Book)
                        .where(Book.id == book_id)
                        .values(
                            raw_data={"html": html},
                            raw_data_key=key,
                        )
                    )
                logger.info(f"[OK] Book {book_id}: raw_data и raw_data_key обновлены. Ключ: {key}")

            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"[SKIP] HTTP {e.response.status_code} для {book_url} (id={book_id})"
                )
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                logger.error(f"[ERR] Сетевая ошибка для {book_url}: {e}")
            except Exception as e:
                logger.error(f"[ERR] Непредвиденная ошибка для book {book_id}: {e}")


if __name__ == "__main__":
    asyncio.run(update_raw_data())
