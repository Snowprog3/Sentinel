from io import BytesIO

from src.artifact_saver import upload_raw_html
from src.minio_client import ensure_bucket_exists, get_minio_client

BUCKET = "sentinel-raw"

ensure_bucket_exists(BUCKET)

client = get_minio_client()
data = BytesIO(b"Hello, MinIO!")
client.put_object(BUCKET, "test/hello.txt", data, length=data.getbuffer().nbytes)
print("File uploaded.")


key = upload_raw_html(
    42, "<html><body>Test book</body></html>", {"url": "http://books.toscrape.com/test"}
)
print(f"Uploaded with key: {key}")
