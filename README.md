# Sentinel

Учебный проект извлечения данных из веба: загрузчики на **httpx**, сохранение в **PostgreSQL** (SQLAlchemy 2 async, **Alembic**, книги с **`raw_data` JSONB** и ключом **`raw_data_key`** в **MinIO**), **Scrapy**‑проект `bookstore` (Books to Scrape), валидация **Pydantic**, дедупликация URL через **Redis**, метрики **Prometheus**, трассировка **OpenTelemetry** → **Jaeger**.

## Возможности

### Скрипты на httpx (`src/`)

- **Загрузка страниц** — `httpx` (`AsyncClient` и синхронный `Client`), сброс прокси-переменных в `proxy.py`.
- **Файловое хранилище** — сырой HTML в `data/raw/` (каталог в `.gitignore`).
- **Парсинг** — пример в `parser.py`.
- **Ошибки HTTP** — классификация `retry` / `skip` / `abort` в `error_handler.py` (авто‑retry для этих скриптов не подключён).

### Scrapy (`src/bookstore/`)

- **Пауки** — `books` (каталог), `books_detail` (карточки книг + сырой HTML в `raw_data`; при старте генерирует `job_id` для всего прогона).
- **Пайплайны** — оба принимают `(item, spider)` по контракту Scrapy:
  - `ValidationPipeline` — Pydantic: `RawBookItem` → `ParsedBook` → `NormalizedBook`; невалидный URL/цена → `DropItem`.
  - `DatabasePipeline` — Redis → Postgres → MinIO:
    - guard URL (`DropItem`, если URL отсутствует или не строка);
    - Redis `SET NX` (дедуп, TTL 86400 с): дубликат → метрика `duplicate_redis`, insert пропускается;
    - insert в Postgres → upload HTML в MinIO → `UPDATE raw_data_key`;
    - дубликат по unique constraint в БД → метрика `duplicate_db`, item возвращается без падения;
    - метрики со статусами `saved` / `duplicate_redis` / `duplicate_db` / `error`;
    - OTLP-спаны: `save-book`, `redis-check`, `insert_book`, `upload_minio`, `update_bd_key`;
    - счётчик дубликатов Redis и сигнал `spider_closed`.
- **Downloader middleware** — `RetryWithBackoffMiddleware` для части сетевых ошибок Twisted.
- **Расширение** — `PrometheusMetricsExtension`: HTTP‑экспортёр метрик на порту `8000` при старте движка Scrapy.
- **Трассировка** — `trace_id` и `job_id` на item; спаны OTLP в пайплайне (`redis-check`, `insert_book`, `upload_minio` и др.).
- **Выгрузка** — JSON‑фид `FEEDS`: при запуске из `src/bookstore` файл `src/bookstore/data/books.json`.

### Общее

- **БД** — модель `Book` (`title`, `price`, `url`, `raw_data`, `raw_data_key`), `database.py`, `crud.py`, схемы в `schemas.py`.
- **MinIO** — `artifact_saver.py`, `minio_client.py`: bucket `sentinel-raw`, ключи вида `books/{id}/raw_html/...`; дополнительные метаданные объекта принимаются как `Mapping[str, str]`; политики хранения — [docs/retention.md](docs/retention.md), очистка — `cleanup_minio.py`.
- **Redis** — `redis_client.py`: дедуп URL для пайплайна (TTL 86400 с).
- **Метрики** — `metrics.py`: счётчики `sentinel_requests`, `sentinel_errors`, гистограмма `sentinel_request_duration_seconds` (источники `scrapy`, `mini_project` и др.).
- **Наблюдаемость** — в Compose: **Prometheus**, **Grafana**, **Jaeger**, **OTEL Collector**; Scrapy отдаёт метрики на `:8000`, трейсы — в collector по OTLP HTTP.

## Зависимости (основные)

См. [pyproject.toml](pyproject.toml): `httpx`, `loguru`, `parsel`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic`, `pydantic-settings`, `python-dotenv`, `scrapy`, `redis[hiredis]`, `minio`, `prometheus-client`, `uvicorn`, `opentelemetry-api/sdk/exporter-otlp`. Разработка: `pytest`, `pytest-asyncio`, `respx`, `ruff`, `mypy`, `pip-audit`.

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `src/mini_project.py` | Точка входа в Docker по умолчанию: async-загрузка URL из `urls.py`, статистика, запись в `data/raw/`. |
| `src/async_multi_download.py` | Альтернативный async-загрузчик. |
| `src/sync_multi_page.py` | Синхронная загрузка в цикле. |
| `src/parser.py` | Разбор HTML (демо). |
| `src/redis_client.py` | Redis: дедуп URL для Scrapy-пайплайна. |
| `src/utils.py` | Пути и имена файлов из URL, проверка URL. |
| `src/urls.py` | Список тестовых URL для `mini_project`. |
| `src/config.py` | **Pydantic Settings** (`.env`): БД, Redis, MinIO, Grafana, OTEL. |
| `src/database.py` | Async engine и сессии. |
| `src/models.py` | SQLAlchemy-модели (`Book`, JSONB, `raw_data_key`). |
| `src/schemas.py` | Схемы Pydantic (пайплайн, CRUD). |
| `src/crud.py` | Асинхронный CRUD для книг (`get_book_by_title` — одна запись или `None`). |
| `src/artifact_saver.py` | Загрузка raw HTML в MinIO (метаданные через `Mapping[str, str]`). |
| `src/minio_client.py` | Клиент MinIO. |
| `src/cleanup_minio.py` | Удаление устаревших объектов (см. retention). |
| `src/update_raw.py` | Дозагрузка HTML в MinIO для существующих записей в БД. |
| `src/metrics.py` | Метрики Prometheus и запуск HTTP-сервера. |
| `src/metrics_server.py` | ASGI-приложение метрик (uvicorn). |
| `src/otel.py` | Инициализация OTLP-трейсера. |
| `src/tracing.py` | `generate_trace_id()` для пауков и item. |
| `src/sql_practice.py` | Пример операций с БД. |
| `src/jsonb_demo.py` | Пример записи и поиска по `raw_data`. |
| `src/db_check.py` | Простая проверка окружения БД. |
| `src/proxy.py` | Сброс `*_proxy` в окружении. |
| `src/error_handler.py` | Классификация ошибок httpx. |
| `src/bookstore/` | Scrapy: `scrapy.cfg`, пауки, `items`, `pipelines`, `middlewares`, `extensions`, `settings`. |
| `docs/retention.md` | Сроки хранения артефактов MinIO. |
| `migrations/` | Ревизии Alembic. |
| `alembic.ini` | Конфигурация Alembic. |
| `docker-compose.yaml` | `parser`, Postgres, Redis, MinIO, Prometheus, Grafana, Jaeger, OTEL Collector. |
| `prometheus.yml` | Scrape target `localhost:8000` (метрики Scrapy). |
| `otel-collector-config.yaml` | Маршрутизация OTLP → Jaeger. |
| `minio_lifecycle.json` | Пример lifecycle для MinIO. |
| `tests/` | Тесты утилит, парсера, HTTP, схем, Redis, пайплайна (mock `spider`), метрик и др. |
| `scripts/check.sh` | Полная проверка: mypy → ruff → pip-audit → pytest. |
| `run.sh` | Линт → формат → `mini_project`. |

## Требования

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)
- Для Scrapy с записью в БД: **PostgreSQL 15+** (после миграций).
- Для дедупа и полного пайплайна: **Redis**.
- Для сохранения raw HTML: **MinIO** (или сервис `minio` в Compose).
- Для метрик и трейсов в Compose: **Prometheus**, **Grafana**, **Jaeger**, **OTEL Collector** (опционально для локального краула без Docker).

## Быстрый старт (локально)

```bash
git clone <repository-url>
cd sentinel
uv sync
```

Скопируйте [.env.example](.env.example) в `.env` и заполните переменные по [`src/config.py`](src/config.py) (БД, Redis, MinIO, Grafana, OTEL). Миграции:

```bash
uv run alembic upgrade head
```

### Загрузчик httpx (без Scrapy)

`mini_project.py` к БД не обращается. Остальные скрипты и краулер требуют настроенную БД; для полного пайплайна — Redis и MinIO.

```bash
uv run python src/mini_project.py
```

### Scrapy bookstore

Из каталога с `scrapy.cfg` (корень Sentinel на `PYTHONPATH` подставляет `settings.py`):

```bash
cd src/bookstore
uv run scrapy crawl books
# или (сырой HTML в item → MinIO через пайплайн)
uv run scrapy crawl books_detail
```

Перед запуском: Postgres (миграции), Redis, MinIO. При крауле поднимается экспортёр метрик на **http://127.0.0.1:8000/metrics** (порт задаётся `METRICS_PORT` в `settings.py`).

Проверка сети до демо-сайта: `getent hosts books.toscrape.com`.

### Прочее

```bash
uv run python src/sql_practice.py
uv run python src/jsonb_demo.py
uv run python src/cleanup_minio.py   # очистка старых объектов MinIO
chmod +x scripts/check.sh && ./scripts/check.sh   # mypy, ruff, pip-audit, pytest
chmod +x run.sh && ./run.sh
```

## Команды разработки

| Команда | Описание |
|---------|----------|
| `./scripts/check.sh` | mypy, ruff (lint + format), pip-audit, pytest — рекомендуемый прогон перед коммитом |
| `uv run mypy .` | Статическая проверка типов (конфиг в `pyproject.toml`, 49+ файлов) |
| `uv run ruff check .` | Линт |
| `uv run ruff format .` | Форматирование |
| `uv run pytest -v` | Тесты |
| `uv run pip-audit` | Проверка уязвимостей в зависимостях |
| `uv run alembic upgrade head` | Применить миграции |
| `uv run alembic revision --autogenerate -m "описание"` | Новая ревизия |

Конфигурация **mypy**: плагин `pydantic.mypy`, `check_untyped_defs = true`. Scrapy-пайплайны и CRUD типизированы явно (`-> Item`, `-> bool`, `Book | None` и т.д.).

## Docker

Сборка и запуск контейнера приложения (**по умолчанию** `mini_project`, не Scrapy):

```bash
docker build -t sentinel:latest .
docker run --rm -v "$(pwd)/data:/app/data" sentinel:latest
```

**Compose** поднимает:

| Сервис | Назначение | Порты (хост) |
|--------|------------|--------------|
| `parser` | Приложение (образ `sentinel`) | — |
| `db` | PostgreSQL 15 | `5432` |
| `cache` | Redis 7 | `6379` |
| `minio` | S3-совместимое хранилище | `9000`, `9001` (консоль) |
| `prometheus` | Сбор метрик | `9090` (`network_mode: host`) |
| `grafana` | Дашборды | `3000` |
| `jaeger` | UI трейсов | `16686` |
| `otel-collector` | OTLP → Jaeger | `4318` (HTTP) |

Для `parser` в Compose заданы `DB_HOST=db`, `REDIS_HOST=cache`, `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318`; остальное — из `.env`.

```bash
cp .env.example .env
# Заполните DB_*, MINIO_*, GF_*, OTEL_* и при необходимости порты

docker compose up --build
```

Краулер Scrapy **не стартует автоматически**. Пример ручного запуска:

```bash
docker compose exec parser bash -lc "cd /app/src/bookstore && alembic -c /app/alembic.ini upgrade head && scrapy crawl books_detail"
```

Тома: `./data` → `/app/data`, `./logs` → `/app/logs`.

**UI после `docker compose up`:** Grafana — http://localhost:3000, Jaeger — http://localhost:16686, MinIO Console — http://localhost:9001.

## Переменные окружения

Поля **`Settings`** в [`src/config.py`](src/config.py) (файл [`.env.example`](.env.example) может быть неполным — ориентируйтесь на `config.py`):

| Переменная | Назначение |
|------------|------------|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`, `DB_PASS` | PostgreSQL |
| `REDIS_HOST`, `REDIS_PORT` | Redis (`cache` в Compose) |
| `MINIO_USER`, `MINIO_PASS`, `MINIO_HOST`, `MINIO_PORT` | MinIO |
| `GF_USER`, `GF_PASS`, `GF_LOG_LEVEL` | Grafana |
| `OTEL_SERVICE_NAME` | Имя сервиса в трейсах |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP (например `http://otel-collector:4318` в Compose) |
| `REQUEST_TIMEOUT` | Таймаут HTTP для загрузчиков (секунды) |
| `DEBUG` | `true` / `false` |

Файл `.env` не коммитится.

## Ограничения и заметки

- Повторы HTTP для скриптов на **httpx** по политике из `error_handler` не подключены.
- В Scrapy два слоя повторов: встроенный **RetryMiddleware** и **RetryWithBackoffMiddleware**.
- `ValidationPipeline` / `DatabasePipeline`: аргумент `spider` обязателен (контракт Scrapy); в unit-тестах передаётся `MagicMock` (см. `tests/test_pipeline.py`).
- Redis помечает URL обработанным **до** insert в БД (`SET NX`). Если insert падает, ключ остаётся до TTL (86400 с) — повторная обработка того же URL не произойдёт без ручного сброса.
- Дубликат по unique constraint в Postgres не бросает `DropItem` — item возвращается, метрика `duplicate_db`.
- Prometheus в Compose использует `network_mode: host` и скрейпит `localhost:8000` — метрики Scrapy должны быть доступны на хосте при крауле из контейнера `parser`.
- Коллизии имён файлов при массовой загрузке через `mini_project` возможны при росте объёма.
- Учитывайте `robots.txt` и условия использования сайтов при реальных сборах.

## Назначение

Учебная практика Data Extraction / бэкенда: HTTP и async, парсинг (parsel и Scrapy), ORM, миграции, Redis, объектное хранилище, метрики, распределённая трассировка, контейнеры.
