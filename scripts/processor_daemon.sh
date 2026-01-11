#!/usr/bin/env bash

echo "$0 Running processor-daemon"

exec uvicorn processor.processor_daemon:execute \
    --factory \
    --host 0.0.0.0 \
    --port 8000 \
    --proxy-headers
