import time
import logging

from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient
from .utils import get_latest_job_id, process_job, generate_job_id, fetch_new_jobs_from_department, clean_html_for_embedding

logging.basicConfig(level=logging.INFO)
MAX_INITIAL_JOBS = 150
SLEEP_TIME = 1
DEPARTMENT_ID = 57


def process_and_index_new_jobs():
    embedding_client = OpenAIEmbeddingClient()
    es_client = ElasticsearchClient()

    # 1. Get last indexed job ID from metadata
    metadata = es_client.get_metadata("last_ejobs_indexed_id")
    last_indexed_id = metadata.get("value")

    # 2. Get the latest job ID from ejobs
    latest_job_id = get_latest_job_id()
    if not latest_job_id:
        logging.error("❌ Failed to fetch latest job ID from ejobs.ro")
        return
    
    if last_indexed_id is None:
        logging.warning(f"⚠️ No last_ejobs_indexed_id found. Will process last {MAX_INITIAL_JOBS} jobs.")
        last_indexed_id = max(0, latest_job_id - MAX_INITIAL_JOBS)

    logging.info(f"Scraping jobs from ID {latest_job_id} down to {last_indexed_id + 1}")
    newest_scraped_id = latest_job_id

    current_id = latest_job_id
    while current_id > last_indexed_id:
        job = process_job(current_id)
        current_id -= 1

        if not job:
            continue

        try:
            # 3. Add embedding
            embedding_description = clean_html_for_embedding(job["description"])
            embedding_input = f"{job['job_title']}\n{embedding_description}\n{job['meta_tags']}"
            embedding_response = embedding_client.create(embedding_input)
            job["embedding"] = embedding_response.data[0].embedding

            job.pop("meta_tags", None)

            # 6. Generate document _id
            doc_id = generate_job_id(job)

            # 7. Save to Elasticsearch
            es_client.index_job(doc_id, job)
            logging.info(f"✅ Indexed job {job['site_id']} | {job['job_title']}")

            time.sleep(SLEEP_TIME)

        except Exception as e:
            logging.error(f"❌ Failed to process/index job {job.get('site_id')}: {e}")

    # 8. Save newest job ID from this session into metadata
    es_client.update_metadata("last_ejobs_indexed_id", {"value": newest_scraped_id})
    logging.info(f"✅ Updated metadata: last_ejobs_indexed_id = {newest_scraped_id}")


def process_and_index_jobs_from_department():
    embedding_client = OpenAIEmbeddingClient()
    es_client = ElasticsearchClient()

    # Get last indexed job ID for department 57
    metadata = es_client.get_metadata("last_ejobs_dept57_indexed_id")
    last_indexed_id = metadata.get("value")

    if last_indexed_id is None:
        logging.warning("⚠️ No last_ejobs_dept57_indexed_id found. Fetching last 300 jobs.")
        last_indexed_id = 0  # treat as no last ID, so fetch last 100 jobs

    jobs = fetch_new_jobs_from_department(DEPARTMENT_ID, last_indexed_id, max_jobs=300)
    logging.info(f"Total new jobs fetched for department {DEPARTMENT_ID}: {len(jobs)}")

    if not jobs:
        logging.info("No new jobs to process.")
        return

    # Sort jobs ascending by id so we index from oldest to newest
    jobs.sort(key=lambda x: x["id"])

    newest_job_id = last_indexed_id
    for job_summary in jobs:
        job_id = job_summary["id"]
        job = process_job(job_id)
        if not job:
            logging.info(f"Skipping job {job_id} after detailed processing/filtering")
            continue

        try:
            embedding_description = clean_html_for_embedding(job["description"])
            embedding_input = f"{job['job_title']}\n{embedding_description}\n{job['meta_tags']}"
            embedding_response = embedding_client.create(embedding_input)
            job["embedding"] = embedding_response.data[0].embedding

            job.pop("meta_tags", None)

            doc_id = generate_job_id(job)
            es_client.index_job(doc_id, job)
            logging.info(f"✅ Indexed job {job['site_id']} | {job['job_title']}")

            if job_id > newest_job_id:
                newest_job_id = job_id

            time.sleep(SLEEP_TIME)
        except Exception as e:
            logging.error(f"❌ Failed to index job {job.get('site_id')}: {e}")

    # Update the last indexed job ID in metadata
    es_client.update_metadata("last_ejobs_dept57_indexed_id", {"value": newest_job_id})
    logging.info(f"✅ Updated metadata: last_ejobs_dept57_indexed_id = {newest_job_id}")


if __name__ == "__main__":
    # process_and_index_new_jobs()
    process_and_index_jobs_from_department()
