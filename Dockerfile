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
ARG UID=1000
ARG GID=1000
RUN addgroup --gid $GID app && adduser --uid $UID --gid $GID app
# Копируем весь остальной код проекта
COPY --chown=app:app . .
# Копируем созданное на этапе builder виртуальное окружение в финальный образ
# Копируем из стадии builder папку /app/.venv в текущую папку /app/.venv
COPY --from=builder --chown=app:app /app/.venv /app/.venv


# Добавляем папку с виртуальным окружением в PATH, чтобы Python "видел" наши пакеты
ENV PATH="/app/.venv/bin:$PATH"
USER app

# Указываем команду для запуска вашего приложения
CMD ["python", "src/mini_project.py"]