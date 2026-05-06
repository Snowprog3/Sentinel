FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

CMD ["uv", "run", "python", "src/mini_project.py"]
