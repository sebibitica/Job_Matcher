#!/bin/sh
printenv | grep -v "no_proxy" > /etc/container_environment
service cron start
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4