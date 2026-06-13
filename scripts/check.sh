#!/bin/bash


cd ~/projects/sentinel
uv run mypy .
uv run ruff check --fix
uv run ruff format .
uv run pip-audit
uv run pytest -v