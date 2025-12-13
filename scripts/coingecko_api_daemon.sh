#!/usr/bin/env bash

echo "$0 Running coingecko_api_daemon"

export CONSUMER_GROUP_ID=coingecko_api_daemon
exec python /srv/src/gateway/coingecko_api_daemon.py
