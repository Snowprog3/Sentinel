## 1 builder stage

# Use oficial image of Python
FROM python:3.12-slim-bookworm AS builder
# Install uv without cach
RUN pip install --no-cache-dir uv
# Install working directory
WORKDIR /app
# Install files with dependencies for install on tht builder`s stage
COPY pyproject.toml uv.lock ./
# Install dependencies to app/.venv, --no-dev = check not install -dev dependencies
RUN uv sync --no-dev --frozen

## 2 final stage for runtime

FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Создаем непривилегированного пользователя (важно для безопасности!)
RUN addgroup --system app && adduser --system --group app
# Меняем владельца рабочей директории на нашего нового пользователя
RUN chown -R app:app /app

# Копируем созданное на этапе builder виртуальное окружение в финальный образ
# Копируем из стадии builder папку /app/.venv в текущую папку /app/.venv
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Копируем весь остальной код проекта
COPY --chown=app:app . .

# Добавляем папку с виртуальным окружением в PATH, чтобы Python "видел" наши пакеты
ENV PATH="/app/.venv/bin:$PATH"

# Указываем команду для запуска вашего приложения
CMD ["python", "src/mini_project.py"]