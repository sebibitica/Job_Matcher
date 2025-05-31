import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient
from ..preprocessor.preprocessor import TextPreprocessor
from .utils import (
    get_latest_job_id,
    process_job,
    generate_job_id,
    fetch_new_jobs_from_department,
    clean_html_for_embedding,
)

logging.basicConfig(level=logging.INFO)
MAX_INITIAL_JOBS = 100
DEPARTMENT_ID = 57
MAX_WORKERS = 8

embedding_client = OpenAIEmbeddingClient()
es_client = ElasticsearchClient()
text_preprocessor = TextPreprocessor()


def process_single_job(job_id):
    """Process and index a single job by job ID."""
    job = process_job(job_id)
    if not job:
        return None, job_id

    try:
        embedding_description = clean_html_for_embedding(job["description"])
        embedding_input = f"{job['job_title']}\n{embedding_description}\n{job['meta_tags']}"
        preprocessed_description = text_preprocessor.preprocess_job(embedding_input)
        embedding_response = embedding_client.create(preprocessed_description)
        job["embedding"] = embedding_response.data[0].embedding
        job.pop("meta_tags", None)
        doc_id = generate_job_id(job)
        es_client.index_job(doc_id, job)
        logging.info(f"✅ Indexed job {job['site_id']} | {job['job_title']}")
        return job_id, None
    except Exception as e:
        logging.error(f"❌ Failed to process/index job {job.get('site_id')}: {e}")
        return None, job_id


def process_and_index_new_jobs():
    """Process and index new jobs from ejobs.ro in parallel."""
    metadata = es_client.get_metadata("last_ejobs_indexed_id")
    last_indexed_id = metadata.get("value")

    latest_job_id = get_latest_job_id()
    if not latest_job_id:
        logging.error("❌ Failed to fetch latest job ID from ejobs.ro")
        return

    if last_indexed_id is None:
        logging.warning(
            f"⚠️ No last_ejobs_indexed_id found. Will process last {MAX_INITIAL_JOBS} jobs."
        )
        last_indexed_id = max(0, latest_job_id - MAX_INITIAL_JOBS)
    elif last_indexed_id >= latest_job_id:
        logging.info(
            f"✅ No new jobs to process. Last indexed job ID {last_indexed_id} is up to date."
        )
        return

    logging.info(
        f"Scraping jobs from ID {latest_job_id} down to {last_indexed_id + 1}"
    )
    newest_scraped_id = latest_job_id

    job_ids = list(range(latest_job_id, last_indexed_id, -1))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_single_job, job_id): job_id for job_id in job_ids
        }
        for future in as_completed(futures):
            job_id, failed_id = future.result()

    es_client.update_metadata("last_ejobs_indexed_id", {"value": newest_scraped_id})
    logging.info(f"✅ Updated metadata: last_ejobs_indexed_id = {newest_scraped_id}")


def process_single_department_job(job_summary):
    """Process and index a single job from a department."""
    job_id = job_summary["id"]
    job = process_job(job_id)
    if not job:
        logging.info(f"Skipping job {job_id}: not found or empty.")
        return None, job_id

    try:
        embedding_description = clean_html_for_embedding(job["description"])
        embedding_input = f"{job['job_title']}\n{embedding_description}\n{job['meta_tags']}"
        preprocessed_description = text_preprocessor.preprocess_job(embedding_input)
        embedding_response = embedding_client.create(preprocessed_description)
        job["embedding"] = embedding_response.data[0].embedding
        job.pop("meta_tags", None)
        doc_id = generate_job_id(job)
        es_client.index_job(doc_id, job)
        logging.info(f"✅ Indexed job {job['site_id']} | {job['job_title']}")
        return job_id, None
    except Exception as e:
        logging.error(f"❌ Failed to index job {job.get('site_id')}: {e}")
        return None, job_id


def process_and_index_jobs_from_department():
    """Process and index new jobs from a specific department in parallel."""
    metadata = es_client.get_metadata("last_ejobs_dept57_indexed_id")
    last_indexed_id = metadata.get("value")

    if last_indexed_id is None:
        logging.warning(
            "⚠️ No last_ejobs_dept57_indexed_id found. Fetching last 300 jobs."
        )
        last_indexed_id = 0

    jobs = fetch_new_jobs_from_department(DEPARTMENT_ID, last_indexed_id, max_jobs=300)
    logging.info(
        f"Total new jobs fetched for department {DEPARTMENT_ID}: {len(jobs)}"
    )

    if not jobs:
        logging.info("No new jobs to process.")
        return

    jobs.sort(key=lambda x: x["id"])
    newest_job_id = last_indexed_id

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_single_department_job, job_summary): job_summary["id"]
            for job_summary in jobs
        }
        for future in as_completed(futures):
            job_id, failed_id = future.result()
            if job_id and job_id > newest_job_id:
                newest_job_id = job_id

    es_client.update_metadata("last_ejobs_dept57_indexed_id", {"value": newest_job_id})
    logging.info(
        f"✅ Updated metadata: last_ejobs_dept57_indexed_id = {newest_job_id}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job processing options")
    parser.add_argument(
        "--mode",
        choices=["all", "department", "both"],
        default="all",
        help="Which job processing to run: all (default), department, or both"
    )
    args = parser.parse_args()

    if args.mode == "all":
        process_and_index_new_jobs()
    elif args.mode == "both":
        process_and_index_new_jobs()
        process_and_index_jobs_from_department()
    elif args.mode == "department":
        process_and_index_jobs_from_department()