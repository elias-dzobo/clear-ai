#!/bin/bash 

set -e 

echo "Starting Clear AI..."

exec gunicorn api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000