from minio import Minio

from src.config import settings

_client = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_USER,
            secret_key=settings.MINIO_PASS,
            secure=False,  # для локальной разработки
        )
    return _client


def ensure_bucket_exists(bucket_name: str) -> None:
    client = get_minio_client()
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")
