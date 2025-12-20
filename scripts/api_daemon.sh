#!/usr/bin/env bash

echo "$0 Running api-daemon"

exec uvicorn api.api_daemon:execute \
    --factory \
    --host 0.0.0.0 \
    --port 8000 \
    --proxy-headers
