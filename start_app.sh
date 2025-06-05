#!/bin/bash

# colors for output
GREEN='\033[0;32m'
NC='\033[0m' # no Color


BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$BASE_DIR/job_matcher_backend"
FRONTEND_DIR="$BASE_DIR/job_matcher_frontend"

if [ -f "$BASE_DIR/.env" ]; then
    set -a
    source "$BASE_DIR/.env"
    set +a
else
    echo -e "${GREEN}No .env file found at $BASE_DIR/.env${NC}"
    exit 1
fi

#override these variables for local development
export ELASTICSEARCH_URL="http://localhost:9200"
export VITE_API_URL="http://localhost:8000"

LOG_DATE=$(date +%Y-%m-%d)
LOG_DIR="$BASE_DIR/logs/$LOG_DATE"
mkdir -p "$LOG_DIR"

# Create new log file with timestamp
LOG_FILE="$LOG_DIR/backend_$(date +%H%M%S).log"
touch "$LOG_FILE"

echo -e "${GREEN}Starting Job Matcher application...${NC}"

echo -e "${GREEN}Starting Docker containers...${NC}"
cd "$BACKEND_DIR"
docker-compose up -d

echo -e "${GREEN}Waiting for containers to be ready...${NC}"
sleep 10


echo -e "${GREEN}Starting backend API...${NC}"
cd "$BACKEND_DIR"
source venv/bin/activate

nohup uvicorn api:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --reload \
    --no-access-log \
    > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!
deactivate



echo -e "${GREEN}Starting frontend...${NC}"
cd "$FRONTEND_DIR"
nohup npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

# Function to kill processes and cleanup
cleanup() {
    echo -e "${GREEN}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    docker-compose -f "$BACKEND_DIR/docker-compose.yml" down
    exit
}

# Register the cleanup function to run on script termination
trap cleanup INT TERM

echo -e "${GREEN}All services started successfully!${NC}"
echo "Logs are available in:"
echo "$BASE_DIR/logs/"
echo "Press Ctrl+C to stop all services"

# Keep script running and show tail of logs
tail -f "$LOG_FILE"