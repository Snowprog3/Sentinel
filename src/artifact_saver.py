import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from io import BytesIO

from src.minio_client import get_minio_client

BUCKET = "sentinel-raw"


def generate_object_key(book_id: int, artifact_type: str, extension: str = "html") -> str:
    """Генерирует уникальный ключ объекта в MinIO."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    random_suffix = uuid.uuid4().hex[:6]
    return f"books/{book_id}/{artifact_type}/{timestamp}_{random_suffix}.{extension}"


def upload_raw_html(book_id: int, html: str, metadata: Mapping[str, str] | None = None) -> str:
    """Загружает raw HTML в MinIO и возвращает ключ объекта."""
    client = get_minio_client()
    key = generate_object_key(book_id, "raw_html", "html")
    data = BytesIO(html.encode("utf-8"))

    full_metadata = {
        "book_id": str(book_id),
        "content_type": "text/html",
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    if metadata:
        full_metadata.update(metadata)

    upload_metadata: dict[str, str | list[str] | tuple[str]] = {
        key: value for key, value in full_metadata.items()
    }

    client.put_object(
        BUCKET,
        key,
        data,
        length=data.getbuffer().nbytes,
        content_type="text/html",
        metadata=upload_metadata,
    )
    print(f"Uploaded raw HTML for book {book_id} to {key}")
    return key
