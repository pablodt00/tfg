#!/usr/bin/env bash

echo "$0 Running webapp-daemon"

exec streamlit run src/app/webapp_daemon.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true
