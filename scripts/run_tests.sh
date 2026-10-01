#!/usr/bin/env bash
set -e
echo "========================================================"
echo "Running NexoraNet Full Test Suite"
echo "========================================================"

SCRIPT_DIR="$(dirname "$0")"

echo "[1/3] Running Backend Ruff Lint Check..."
cd "$SCRIPT_DIR/../backend"
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
ruff check app tests

echo "[2/3] Running Backend Pytest Suite..."
pytest tests -v

echo "[3/3] Running Frontend Vitest Suite..."
cd "$SCRIPT_DIR/../frontend"
npm test

echo "========================================================"
echo "All NexoraNet tests passed successfully!"
echo "========================================================"
