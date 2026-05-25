import logging
import time

from scrapy import Item, Spider, signals
from scrapy.exceptions import DropItem
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from src.artifact_saver import upload_raw_html
from src.crud import insert_book
from src.database import AsyncSessionLocal, engine
from src.metrics import ERRORS, REQUEST_DURATION, REQUESTS
from src.models import Book
from src.otel import tracer
from src.redis_client import is_url_processed
from src.schemas import BookCreate, NormalizedBook, ParsedBook, RawBookItem

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """Проверяет и очищает данные через трёхуровневые Pydantic-контракты."""

    def process_item(self, item: Item, spider: Spider) -> Item:
        # 1. Сохраняем сырые данные
        raw = RawBookItem(**dict(item))

        try:
            # 2. Очистка и валидация
            parsed = ParsedBook(
                title=raw.title,
                price=raw.price,
                url=raw.url,
            )
        except Exception as e:
            logger.warning(f"Dropped {item.get('url')}: {e}")
            ERRORS.labels(source="scrapy", error_type="validate").inc()
            raise DropItem(f"Validation failed: {e}")

        # 3. Нормализация
        norm = NormalizedBook(
            title=parsed.title,
            price=parsed.price,
            url=str(parsed.url),
            raw_data=item.get("raw_data"),
        )

        # 4. Обновляем Item очищенными значениями
        item["title"] = norm.title
        item["price"] = str(norm.price) if norm.price else None
        item["url"] = norm.url
        # raw_data оставляем как есть, он уже словарь или None

        logger.info(f"Validated: {norm.title}")
        return item


class DatabasePipeline:
    """Сохраняет валидные книги в PostgreSQL и загружает сырой HTML в MinIO."""

    def __init__(self):
        self.duplicates_skipped = 0

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    async def spider_closed(self, spider):
        logger.info(f"Total duplicates skipped: {self.duplicates_skipped}")

    async def _save_book(self, item: Item, spider: Spider) -> None:
        trace_id = item["trace_id"] if "trace_id" in item else "unknown"
        job_id = spider.job_id if hasattr(spider, "job_id") else "unknown"
        url = item.get("url")

        with tracer.start_as_current_span("save-book") as span:
            span.set_attribute("book_url", url)
            span.set_attribute("trace_id", trace_id)

            # Проверка Redis: если URL уже обработан, пропускаем
            with tracer.start_as_current_span("redis-check") as redis_span:
                redis_span.set_attribute("redis_key", url)
                if await is_url_processed(url):
                    self.duplicates_skipped += 1
                    logger.info(f"[{item['trace_id']}] Skipped duplicate (Redis): {url}")
                    return

            # Создаём Pydantic-схему для вставки
            with tracer.start_as_current_span("insert_book") as db_span:
                db_span.set_attribute("db.operation", "INSERT")
                book_data = BookCreate(
                    title=item.get("title"),
                    price=item.get("price"),
                    url=url,
                    raw_data=item.get("raw_data"),
                )

                async with AsyncSessionLocal() as session:
                    # Вставляем книгу в БД
                    inserted_book = await insert_book(session, book_data)

                # Загружаем сырой HTML в MinIO, если он есть
                raw_html = (item.get("raw_data") or {}).get("html", "")
                if raw_html:
                    with tracer.start_as_current_span("upload_minio") as minio_span:
                        minio_span.set_attribute("minio.bucket", "sentinel_raw")
                        try:
                            key = upload_raw_html(
                                inserted_book.id,
                                raw_html,
                                {
                                    "url": url,
                                    "source": spider.name,
                                    "trace_id": trace_id,
                                    "job_id": job_id,
                                },  # noqa
                            )
                            updated_raw_data = {
                                **item.get("raw_data", {}),
                                "trace_id": trace_id,
                                "job_id": job_id,
                            }  # noqa
                            # Сохраняем ключ MinIO в БД
                            with tracer.start_as_current_span("update_bd_key") as update_span:
                                update_span.set_attribute("db.operation", "UPDATE")
                                async with engine.begin() as conn:
                                    await conn.execute(
                                        update(Book)
                                        .where(Book.id == inserted_book.id)
                                        .values(raw_data=updated_raw_data, raw_data_key=key)
                                    )
                            logger.info(f"Uploaded HTML to MinIO with key {key}")
                        except Exception as e:
                            logger.error(f"MinIO upload failed for book {inserted_book.id}: {e}")
                            ERRORS.labels(source="scrapy", error_type="minio_upload").inc()

    async def process_item(self, item: Item, spider: Spider) -> Item:
        start = time.monotonic()
        status = "error"
        try:
            was_duplicate = await self._save_book(item, spider)
            status = "duplicate_redis" if was_duplicate else "saved"
            logger.info(f"[{item['trace_id']}] Saved to DB and MinIO")
            return item
        except IntegrityError:
            status = "duplicate_db"
            ERRORS.labels(source="scrapy", error_type="duplicate").inc()
            logger.warning(f"Duplicate skipped (DB): {item.get('url')}")
        except Exception as e:
            error_label = type(e).__name__ or "unknown"  # ← гарантируем непустую строку
            ERRORS.labels(source="scrapy", error_type=error_label).inc()
            logger.error(f"Failed to save {item.get('title')}: {e}")
            raise DropItem(f"Database error = {e}")
        finally:
            REQUESTS.labels(source="scrapy", status=status).inc()
            REQUEST_DURATION.labels(source="scrapy", status=status).observe(time.monotonic() - start)

