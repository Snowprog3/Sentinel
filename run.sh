#!/bin/bash
set -euo pipefail

echo "Launch linting code..."
uv run ruff check --fix .

echo "Launch format code..."
uv run ruff format .
echo ""


echo "Launch parser..."
python3 src/async_multi_download.py
echo "Done"