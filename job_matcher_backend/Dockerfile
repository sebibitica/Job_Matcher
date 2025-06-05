FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl cron && apt-get clean && rm -rf /var/lib/apt/lists/*


# Copy application code
COPY . .

# Copy cron jobs file
COPY cron_jobs.txt /etc/cron.d/cron_jobs
RUN chmod 0644 /etc/cron.d/cron_jobs && crontab /etc/cron.d/cron_jobs

# Create log file for cron jobs
RUN touch /var/log/jobs_processor.log

# expose application port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

RUN chmod +x /app/run_backend_with_env.sh

# Start cron in the background, then run uvicorn
CMD ["/app/run_backend_with_env.sh"]