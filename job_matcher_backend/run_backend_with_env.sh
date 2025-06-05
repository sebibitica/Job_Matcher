#!/bin/sh
printenv | grep -v "no_proxy" > /etc/container_environment

# Wait for Elasticsearch
echo "Waiting for Elasticsearch..."
until curl -s http://elasticsearch:9200 | grep -q '"tagline" : "You Know, for Search"'; do
  echo "Elasticsearch not ready. Retrying..."
  sleep 2
done

echo "Elasticsearch is ready!"

service cron start
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4