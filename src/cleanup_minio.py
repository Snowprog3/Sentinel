from datetime import datetime, timedelta, timezone

from src.minio_client import get_minio_client

BUCKET = "sentinel-raw"


def cleanup_old_objects(artifact_type: str, retention_days: int) -> int:
    """Delete objects oldef than retention days for artifact_type"""
    client = get_minio_client()
    prefix = "books/"
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted = 0

    objects = client.list_objects(BUCKET, prefix=prefix, recursive=True)
    for obj in objects:
        if obj.last_modified < cutoff:
            client.remove_object(BUCKET, obj.object_name)
            print(f"Deleted {obj.object_name}")
            deleted += 1

    return deleted


if __name__ == "__main__":
    print("Clean up old raw objects older than > 30 days")
    count = cleanup_old_objects("raw_html", 30)
    print(f"Deleted {count} objects.")
