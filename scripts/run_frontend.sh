#!/usr/bin/env bash
set -e
echo "Starting NexoraNet Vite Frontend..."
cd "$(dirname "$0")/../frontend"
npm run dev
