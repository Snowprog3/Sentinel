# Sentinel

Учебный проект извлечения данных из веба: помимо загрузчиков на **httpx** и сохранения в **PostgreSQL** (SQLAlchemy 2 async, **Alembic**, книги с **`raw_data` JSONB**), в репозитории есть **Scrapy**‑проект `bookstore` — сбор с [Books to Scrape](https://books.toscrape.com), валидация **Pydantic**, дедупликация по URL через **Redis** (`SET` с `NX` и TTL) и запись в ту же модель книг в БД.

## Возможности

### Скрипты на httpx (`src/`)

- **Загрузка страниц** — `httpx` (`AsyncClient` и синхронный `Client`), сброс прокси-переменных в `proxy.py`.
- **Файловое хранилище** — сырой HTML в `data/raw/` (каталог в `.gitignore`).
- **Парсинг** — пример в `parser.py`.
- **Ошибки HTTP** — классификация `retry` / `skip` / `abort` в `error_handler.py` (авто‑retry для этих скриптов не подключён).

### Scrapy (`src/bookstore/`)

- **Пауки** — `books`, `books_detail` (демо-сайт).
- **Пайплайны** — `ValidationPipeline` (нормализация полей, `DropItem` при ошибке валидации), `DatabasePipeline` (Redis → вставка в Postgres, счётчик дубликатов, сигнал `spider_closed`).
- **Downloader middleware** — `RetryWithBackoffMiddleware` для части сетевых ошибок Twisted с паузой и jitter (параллельно со встроенным `RetryMiddleware` Scrapy).
- **Выгрузка** — JSON‑фид по настройке `FEEDS`: при запуске из каталога `src/bookstore` файл будет в `src/bookstore/data/books.json`.

### Общее

- **БД** — модель `Book` (`title`, `price`, `url`, `raw_data`), `database.py`, `crud.py`, схемы в `schemas.py`.
- **Миграции** — Alembic, ревизии в `migrations/versions/`.
- **Redis** — `src/redis_client.py`: проверка/фиксация обработанного URL для пайплайна (TTL 86400 с).

## Зависимости (основные)

См. [pyproject.toml](pyproject.toml): `httpx`, `loguru`, `parsel`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic`, `pydantic-settings`, `python-dotenv`, **`scrapy`**, **`redis[hiredis]`**. Разработка: `pytest`, `pytest-asyncio`, `respx`, `ruff`.

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
| `src/config.py` | Настройки **Pydantic Settings** (`.env`), в т.ч. `DATABASE_URL`. |
| `src/database.py` | Async engine и сессии. |
| `src/models.py` | SQLAlchemy-модели (`Book`, JSONB). |
| `src/schemas.py` | Схемы Pydantic (в т.ч. для пайплайна и CRUD). |
| `src/crud.py` | Асинхронный CRUD для книг. |
| `src/sql_practice.py` | Пример операций с БД. |
| `src/jsonb_demo.py` | Пример записи и поиска по `raw_data`. |
| `src/db_check.py` | Простая проверка окружения БД. |
| `src/proxy.py` | Сброс `*_proxy` в окружении. |
| `src/error_handler.py` | Классификация ошибок httpx. |
| `src/bookstore/` | Scrapy-проект: `scrapy.cfg`, пакет `bookstore` (пауки, `items`, `pipelines`, `middlewares`, `settings`). |
| `migrations/` | Ревизии Alembic. |
| `alembic.ini` | Конфигурация Alembic. |
| `tests/` | Тесты утилит, парсера, HTTP, схем, Redis-клиента, пайплайна валидации и др. |
| `run.sh` | Линт → формат → `mini_project`. |
| `docker-compose.yaml` | Сервис `parser` + Postgres + Redis. |

## Требования

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)
- Для скриптов с БД, Alembic и Scrapy-пайплайна с записью в Postgres: **PostgreSQL 15+**.
- Для полного цикла краулера с дедупом: **Redis** (или сервис `cache` в Compose).

## Быстрый старт (локально)

```bash
git clone <repository-url>
cd sentinel
uv sync
```

Скопируйте [.env.example](.env.example) в `.env` и заполните переменные (как минимум все поля из [`src/config.py`](src/config.py)). Миграции:

```bash
uv run alembic upgrade head
```

### Загрузчик httpx (без Scrapy)

`mini_project.py` к БД не обращается и не требует `.env` для своей работы. Остальные скрипты и краулер — требуют настроенную БД (и Redis для дедупа в пайплайне).

```bash
uv run python src/mini_project.py
```

### Scrapy bookstore

Из каталога с `scrapy.cfg` (родительский пакет `bookstore` на `PYTHONPATH`, путь к корню Sentinel подставляет `settings.py`):

```bash
cd src/bookstore
uv run scrapy crawl books
# или
uv run scrapy crawl books_detail
```

Перед этим должны быть доступны Postgres (после миграций) и Redis. При проблемах с DNS/сетью проверьте: `getent hosts books.toscrape.com` и доступ по HTTP до старта краула.

### Прочее

```bash
uv run python src/sql_practice.py
uv run python src/jsonb_demo.py
chmod +x run.sh && ./run.sh
```

## Команды разработки

| Команда | Описание |
|---------|----------|
| `uv run ruff check .` | Линт |
| `uv run ruff format .` | Форматирование |
| `uv run pytest -v` | Тесты |
| `uv run alembic upgrade head` | Применить миграции |
| `uv run alembic revision --autogenerate -m "описание"` | Новая ревизия |

## Docker

Сборка и запуск контейнера приложения (**по умолчанию выполняется** `mini_project`, не Scrapy):

```bash
docker build -t sentinel:latest .
docker run --rm -v "$(pwd)/data:/app/data" sentinel:latest
```

**Compose** поднимает `parser`, `db` (Postgres) и `cache` (Redis). В `docker-compose.yaml` для `parser` задаются `DB_HOST=db`, `DB_PORT=5432`, `REDIS_HOST=cache`; остальное — из `.env`.

```bash
cp .env.example .env
# Заполните DB_USER, DB_NAME, DB_PASS и при необходимости порты Redis

docker compose up --build
```

Краулер Scrapy внутри Compose **не запускается автоматически**; можно выполнить вручную, например:

```bash
docker compose exec parser bash -lc "cd /app/src/bookstore && alembic -c /app/alembic.ini upgrade head && scrapy crawl books"
```

Тома: `./data` → `/app/data`, `./logs` → `/app/logs`.

## Переменные окружения

Файл [`.env.example`](.env.example) должен соответствовать полям **`Settings`** в [`src/config.py`](src/config.py):

| Переменная | Назначение |
|------------|------------|
| `DB_HOST` | Хост PostgreSQL (`localhost` локально, `db` в Compose) |
| `DB_PORT` | Порт, обычно `5432` |
| `DB_USER` | Пользователь БД |
| `DB_NAME` | Имя базы |
| `DB_PASS` | Пароль |
| `REDIS_HOST` | Хост Redis (`localhost` локально, `cache` в Compose) |
| `REDIS_PORT` | Порт Redis, например `6379` |
| `REQUEST_TIMEOUT` | Таймаут HTTP (секунды), для загрузчиков |
| `DEBUG` | `true` / `false` |

Файл `.env` не коммитится.

## Ограничения и заметки

- Повторы HTTP для скриптов на **httpx** по политике из `error_handler` по-прежнему не подключены.
- В Scrapy два слоя повторов: встроенный **RetryMiddleware** и кастомный **RetryWithBackoffMiddleware** — при желании можно сузить исключения в `RETRY_EXCEPTIONS`.
- После успешной проверки URL в Redis и ошибки вставки в БД ключ в Redis уже может быть установлен до истечения TTL — при необходимости понадобится согласованный откат сценариев повторной обработки.
- Коллизии имён файлов при массовой загрузке через `mini_project` возможны при росте объёма.
- Учитывайте `robots.txt` и условия использования сайтов при реальных сборах.

## Назначение

Учебная практика Data Extraction / бэкенда: HTTP и async, парсинг (parsel и Scrapy), ORM, миграции, Redis, контейнеры.
