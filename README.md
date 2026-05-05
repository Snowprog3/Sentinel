# Sentinel

Распределенный агрегатор данных и система мониторинга
Учебный проект для освоения профессии Data Extraction Engineer


## Opportunities

- асинхронная и синхронная загрузка веб-страниц;
- сохранение raw HTML в локальном хранилище;
- классификация HTTP-ошибок и автоматический выбор действий (retry, abort, skip);
- полный набор unit, -mock тестов;
- линтинг и форматирование кода через ruff.


## Quick start

1. Installing uv (https://docs.astral.sh/uv/)
2. Clone repo
       ```bash
   git clone <url>
   cd sentinel

3. Install dependinces 
    `uv sync`

4. Launch asynchronyous downloader:
```bash
./run.sh

# Structura of projects
`src/` - primary code of parser
`tests/` - tests
    `fixtures/` - etalon files for test`s regression
`data/raw/` - download page (not commit)
`./run.sh` - launch script with linting and formater ruff

## Команды разработки

| Команда | Описание |
|---------|----------|
| `uv run ruff check .` | Проверка кода линтером |
| `uv run ruff format .` | Форматирование кода |
| `uv run pytest -v` | Запуск всех тестов |
| `uv run python src/async_multi_download.py` | Запуск асинхронного парсера |
| `uv run python src/first_request.py` | Запуск синхронного парсера |
| `./run.sh` | Полный цикл: линтинг → форматирование → запуск |

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните реальными значениями (если потребуется).
Сейчас проект работает без дополнительных переменных, но структура готова для будущих интеграций.



