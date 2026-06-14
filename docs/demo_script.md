# Demo script — Защита Q1 Sentinel

## 1. Контекст (1–2 мин)
- Sentinel — учебный проект распределённого сбора данных.
- Цель Q1: написать парсер, сохраняющий данные в PostgreSQL и MinIO, с observability (Prometheus + Jaeger) и автоматическим запуском.
- Стек: Python 3.12, Scrapy, SQLAlchemy async, Redis, MinIO, Docker Compose.

## 2. Запуск инфраструктуры (2 мин)
```bash
cd ~/projects/sentinel
docker compose up -d
docker compose ps

Показать, что все сервисы healthy.
3. Ручной запуск паука (2 мин)
bash

docker compose run --rm parser bash -c "cd /app/src/bookstore && scrapy crawl books_detail"

Показать логи: Crawled (200), Validated: ..., Saved to DB and MinIO.
4. Observability (3 мин)

    Метрики: http://localhost:9090 → sentinel_requests_total, sentinel_errors.

    Трейсы: http://localhost:16686 → поиск по sentinel, показать спаны save-book, insert_book, upload_minio.

    Логи: docker compose logs parser | grep <trace_id> — сквозная связка metric → trace → log.

5. Учебный инцидент (2 мин)
bash

docker compose stop minio
docker compose run --rm parser bash -c "cd /app/src/bookstore && scrapy crawl books_detail"

Показать рост метрики sentinel_errors{error_type="minio_upload"}, найти trace_id, трейс в Jaeger, причину в логах.
bash

docker compose start minio

6. Автоматический запуск (1 мин)
bash

systemctl --user status sentinel-crawl.timer
journalctl --user -u sentinel-crawl.service -e

Показать, что парсер запускается по расписанию без рук.
7. Документация и архитектура (1 мин)

    C4: docs/c4/container.puml (показать диаграмму).

    ADR: docs/adr/001-postgres-jsonb.md (объяснить выбор JSONB).

    Runbook: docs/runbook.md (инструкция по эксплуатации).

8. Итоги и планы (1 мин)

    Что сделано в Q1: парсер, хранение, observability, автоматизация, документация.

    Бэклог на Q2: браузерный рендеринг (Playwright), обход Cloudflare (lab), прокси-пул.

text


