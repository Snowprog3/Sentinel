# Sentinel

Учебный проект по извлечению данных с веба: асинхронная и синхронная загрузка HTML, разбор **parsel**, сохранение на диск и **персистенция в PostgreSQL** (SQLAlchemy 2 async + **Alembic**, модель книг с полем **JSONB** и GIN-индексом). В **Docker Compose** поднимаются приложение, Postgres и Redis (к Redis в коде пока нет обращений — задел под очереди и кэш).

## Возможности

- **Загрузка страниц** — `httpx` (`AsyncClient` и синхронный `Client`), сброс прокси-переменных окружения перед запросами.
- **Файловое хранилище** — сырой HTML в `data/raw/` (каталог в `.gitignore`).
- **Парсинг** — пример извлечения полей с демо-сайта (`src/parser.py`).
- **БД** — модель `Book` (`title`, `price`, `url`, `raw_data` JSONB), асинхронный слой `database.py`, операции в `crud.py`, схемы **Pydantic** в `schemas.py`.
- **Миграции** — Alembic, ревизии в `migrations/versions/`.
- **Ошибки HTTP** — классификация `retry` / `skip` / `abort` в `error_handler.py` (автоматические повторы запросов по этой логике не реализованы).
- **Тесты** — `pytest`, `pytest-asyncio`, HTTP-моки `respx`; фикстуры в `tests/fixtures/`.
- **Инфраструктура** — Docker (multi-stage), `docker-compose.yaml`, непривилегированный пользователь в образе.

## Зависимости (основные)

См. [pyproject.toml](pyproject.toml): `httpx`, `loguru`, `parsel`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic`, `pydantic-settings`, `python-dotenv`. Разработка: `pytest`, `respx`, `ruff`.

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `src/mini_project.py` | Точка входа по умолчанию в Docker: async-загрузка URL из `urls.py`, статистика, запись в `data/raw/`. |
| `src/async_multi_download.py` | Альтернативный async-загрузчик. |
| `src/sync_multi_page.py` | Синхронная загрузка в цикле. |
| `src/parser.py` | Разбор HTML (демо). |
| `src/utils.py` | Пути и имена файлов из URL, проверка URL. |
| `src/urls.py` | Список тестовых URL. |
| `src/config.py` | Настройки через **Pydantic Settings** (`.env`), в т.ч. `DATABASE_URL`. |
| `src/database.py` | `create_async_engine`, `AsyncSessionLocal` для рабочих скриптов с БД. |
| `src/models.py` | SQLAlchemy-модели (`Book`, JSONB). |
| `src/schemas.py` | Pydantic-схемы для CRUD. |
| `src/crud.py` | Асинхронные операции с сессией. |
| `src/sql_practice.py` | Пример: вставка, выборка, обновление, подсчёт. |
| `src/jsonb_demo.py` | Пример записи и поиска по полям `raw_data`. |
| `src/db_check.py` | Простая проверка: `create_all`, вставка тестовой записи (для отладки окружения). |
| `src/proxy.py` | Сброс `*_proxy` в окружении. |
| `src/error_handler.py` | Классификация исключений `httpx`. |
| `migrations/` | Ревизии Alembic; `env.py` использует метаданные моделей из `src.models`. |
| `alembic.ini` | Конфигурация Alembic (`script_location = migrations`). |
| `tests/` | Тесты утилит, парсера, обработчика ошибок, HTTP. |
| `run.sh` | Линт → формат → `mini_project`. |
| `docker-compose.yaml` | Сервис `parser` + Postgres + Redis. |

## Требования

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)
- Локально или в Docker: **PostgreSQL 15+** (для скриптов с БД и миграций).

## Быстрый старт (локально)

```bash
git clone <repository-url>
cd sentinel
uv sync
```

Скопируйте [.env.example](.env.example) в `.env`. Скрипт **`mini_project.py`** к базе не ходит и **`config` не импортирует** — для него файл `.env` не обязателен. Для **`sql_practice`**, **`jsonb_demo`**, **`db_check`**, **Alembic** и любого кода, который тянет `src.config`, нужны **все** переменные из таблицы ниже (как в `Settings`).

Миграции (из корня репозитория, с поднятой БД):

```bash
uv run alembic upgrade head
```

Запуск основного загрузчика:

```bash
uv run python src/mini_project.py
```

Примеры работы с БД (из корня, интерпретатор подхватывает `src/` как пакет путей для скрипта):

```bash
uv run python src/sql_practice.py
uv run python src/jsonb_demo.py
```

Полный цикл из скрипта:

```bash
chmod +x run.sh
./run.sh
```

## Команды разработки

| Команда | Описание |
|---------|----------|
| `uv run ruff check .` | Линт |
| `uv run ruff format .` | Форматирование |
| `uv run pytest -v` | Тесты |
| `uv run alembic upgrade head` | Применить миграции |
| `uv run alembic revision --autogenerate -m "описание"` | Новая ревизия (после правок моделей) |

## Docker

Сборка и запуск только контейнера приложения (как в `Dockerfile` — `mini_project`):

```bash
docker build -t sentinel:latest .
docker run --rm -v "$(pwd)/data:/app/data" sentinel:latest
```

**Compose** поднимает `parser`, `db` (Postgres) и `cache` (Redis). Для `db` в `docker-compose.yaml` используются переменные `DB_USER`, `DB_NAME`, `DB_PASS` из `.env`. Сервис `parser` дополнительно задаёт `DB_HOST=db`, `DB_PORT=5432`, `REDIS_HOST=cache`; остальное подтягивается из `env_file: .env`.

```bash
cp .env.example .env
# Заполните значения (особенно DB_USER, DB_NAME, DB_PASS)

docker compose up --build
```

Тома: `./data` → `/app/data`, `./logs` → `/app/logs`.

## Переменные окружения

Файл [`.env.example`](.env.example) должен совпадать по именам с полями **`Settings`** в [`src/config.py`](src/config.py):

| Переменная | Назначение |
|------------|------------|
| `DB_HOST` | Хост PostgreSQL (`db` внутри Compose) |
| `DB_PORT` | Порт (число), чаще всего `5432` |
| `DB_USER` | Пользователь БД |
| `DB_NAME` | Имя базы |
| `DB_PASS` | Пароль (в Compose передаётся в `POSTGRES_PASSWORD`) |
| `REDIS_HOST` | Хост Redis (`cache` внутри Compose) |
| `REDIS_PORT` | Порт Redis, например `6379` |
| `REQUEST_TIMEOUT` | Таймаут HTTP для будущего использования в загрузчиках, число (секунды) |
| `DEBUG` | `true` / `false` |

Файл `.env` не коммитится.

## Ограничения и направления развития

- Повтор HTTP-запросов по политике из `error_handler` не подключён.
- Нет явного лимита параллелизма загрузки (`Semaphore` / лимиты пула `httpx`) для больших списков URL.
- Логирование: часть кода по-прежнему использует `print`; `loguru` можно использовать единообразно.
- Коллизии имён файлов из URL при массовой загрузке возможны — при росте объёма стоит уникализировать имена (хост, хэш URL).
- Тесты пока не покрывают слой БД и миграции; Redis в Compose не используется кодом приложения.
- CI/CD и нагрузочные прогоны — по желанию.

## Назначение

Проект учебный: практики Data Extraction Engineer и смежного бэкенда (HTTP, async, парсинг, ORM, миграции, контейнеры). Соблюдайте `robots.txt` и правила сайтов при реальных сборах данных.
