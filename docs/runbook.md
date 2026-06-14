# Sentinel Runbook (Q1)

## Запуск и остановка

### Полный стек (Docker Compose)
```bash
cd ~/projects/sentinel
docker compose up -d          # запустить все сервисы
docker compose ps              # проверить состояние
docker compose down            # остановить и удалить контейнеры (тома сохраняются)
docker compose down -v         # остановить и удалить тома (полный сброс данных)

#systemd timer
systemctl --user start sentinel-crawl.timer   # запустить таймер (активирует расписание)
systemctl --user stop sentinel-crawl.timer    # остановить таймер
systemctl --user status sentinel-crawl.timer  # проверить статус
journalctl --user -u sentinel-crawl.service -f # смотреть логи последнего запуска

# manual launch crawl
docker compose run --rm parser bash -c "cd /app/src/bookstore && scrapy crawl books_detail"
# или через скрипт-обёртку:
./scripts/run_crawl.sh

Проверка состояния

    Все сервисы: docker compose ps (все должны быть healthy или running).

    Метрики: http://localhost:9090/graph → запрос sentinel_requests_total.

    Трейсы: http://localhost:16686 → поиск по сервису sentinel.

    Данные в БД: docker compose exec db psql -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM books;".

Объекты в MinIO: http://localhost:9001 → bucket sentinel-raw.

Проверка состояния

    Все сервисы: docker compose ps (все должны быть healthy или running).

    Метрики: http://localhost:9090/graph → запрос sentinel_requests_total.

    Трейсы: http://localhost:16686 → поиск по сервису sentinel.

    Данные в БД: docker compose exec db psql -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM books;".

    Объекты в MinIO: http://localhost:9001 → bucket sentinel-raw.

Типовые проблемы и решения
1. Паук не видит проект Scrapy

Симптом: Scrapy 2.15.2 - no active project
Причина: команда запущена не из директории с scrapy.cfg.
Решение: выполнять cd /app/src/bookstore && scrapy crawl books_detail.
2. MinIO недоступен

Симптом: в логах MinIO upload failed, метрика sentinel_errors{error_type="minio_upload"} растёт.
Решение:
bash

docker compose ps minio          # проверить статус
docker compose restart minio     # перезапустить
docker compose logs minio        # посмотреть логи

После восстановления метрика ошибок перестанет расти.
3. Redis не отвечает

Симптом: паук зависает или падает с ошибкой подключения к Redis.
Решение:
bash

docker compose restart cache

Дедупликация URL временно не работает, но парсер продолжит сбор (дубликаты отсеются на уровне БД).
4. База данных не готова

Симптом: ошибка подключения при старте паука.
Решение: подождать 10–15 секунд после docker compose up -d, пока db станет healthy. Если не помогает — проверить логи: docker compose logs db.
5. Миграции не применены

Симптом: таблицы не найдены (relation "books" does not exist).
Решение:
bash

docker compose run --rm parser bash -c "cd /app && alembic upgrade head"

Восстановление после сбоя

    Перезапустить весь стек:
    bash

    docker compose down && docker compose up -d

    Применить миграции (если требуется).

    Запустить паука вручную и проверить метрики/трейсы.

    Убедиться, что таймер активен: systemctl --user status sentinel-crawl.timer.

text

Проверь команды из runbook на практике:

    Выполни docker compose ps — убедись, что статусы корректны.

    Выполни docker compose logs parser | grep "MinIO upload failed" — сейчас не должно быть ошибок.

    Попробуй ручной запуск паука через скрипт.

Обнови README:
Добавь в оглавление или в раздел «Документация»:
markdown

- [Runbook (эксплуатация)](docs/runbook.md)
- [ADR](docs/adr/)


## Известные ограничения (Q1)

- **Автоматическое восстановление:** systemd timer пока не перезапускает службу при сбое (`Restart=on-failure` не настроен). При отказе Docker или сети парсер не запустится до следующего срабатывания таймера.
- **Миграции:** не выполняются автоматически при запуске контейнера. Требуется ручной запуск `alembic upgrade head`.
- **Дедупликация:** используется optimistic-подход: URL помечается в Redis до успешной вставки в БД. При падении между Redis и PostgreSQL запись теряется, но URL остаётся помеченным как обработанный на 24 часа. В Q2 планируется перейти на идемпотентную вставку.
- **Коллизии имён файлов:** `mini_project.py` генерирует имена файлов на основе URL, при большом количестве однотипных URL возможна перезапись.
- **Логирование:** trace_id добавляется в логи не для всех операций (например, ошибки HTTP в Scrapy-мидлваре логируются без него).
- **Метрики:** не сохраняются между перезапусками контейнера `parser` (т.к. считаются в памяти). Prometheus хранит историю, но при сбросе контейнера часть данных теряется.
