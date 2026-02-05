#!/usr/bin/env bash

echo "🚀 Starting Almira Backend..."

# Start the application with uvicorn
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port ${PORT:-8000} \
  --workers 1 \
  --log-level info \
  --access-log
