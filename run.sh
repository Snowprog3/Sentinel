#!/bin/bash
set -euo pipefail

echo "Launc linting code..."
uv run ruff check src/
echo ""

echo "Launch parser..."
python3 src/first_request.py
echo "Done"