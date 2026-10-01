#!/usr/bin/env bash
set -e
echo "Starting NexoraNet FastAPI Backend..."
cd "$(dirname "$0")/../backend"
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
