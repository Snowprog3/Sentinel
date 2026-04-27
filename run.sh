#!/bin/bash
set -euo pipefail

echo "Launch linting code..."
uv run ruff check --fix src/

echo "\nLaunch format code..."
uv run ruff format src/
echo ""


echo "Launch parser..."
python3 src/async_multi_download.py
echo "Done"