#!/usr/bin/env bash

echo "$0 Running daemon_processor"

export CONSUMER_GROUP_ID=processor-daemon
exec python /srv/src/processor/processor_daemon.py
