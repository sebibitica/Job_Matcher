#!/bin/sh
printenv | grep -v "no_proxy" > /etc/container_environment

if [ -z "$ELASTICSEARCH_URL" ]; then
  echo "ERROR: ELASTICSEARCH_URL is not set."
  exit 1
fi

# Wait for Elasticsearch
echo "Waiting for Elasticsearch ..."
until curl -s "$ELASTICSEARCH_URL" | grep -q '"tagline" : "You Know, for Search"'; do
  echo "Elasticsearch not ready yet. Waiting..."
  sleep 3
done

echo "Elasticsearch is ready!"

service cron start
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
