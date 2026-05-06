#!/bin/bash
set -euo pipefail

echo "Launch linting code..."
uv run ruff check --fix .

echo "Launch format code..."
uv run ruff format .
echo ""

 
echo "Launch parser..."
uv run python3 src/mini_project.py
echo "Done"