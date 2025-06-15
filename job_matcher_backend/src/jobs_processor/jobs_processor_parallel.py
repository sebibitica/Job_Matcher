import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import asyncio
from datetime import datetime

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
MAX_CONCURRENT = 10

embedding_client = OpenAIEmbeddingClient()
es_client = ElasticsearchClient()
text_preprocessor = TextPreprocessor()


async def process_single_job(job_id, semaphore):
    """Process and index a single job by job ID."""
    async with semaphore:
        job = await asyncio.to_thread(process_job, job_id)
        if not job:
            return None, job_id

        try:
            embedding_description = clean_html_for_embedding(job["description"])
            embedding_input = f"{job['job_title']}\n{embedding_description}\n{job['meta_tags']}"
            preprocessed_description = await text_preprocessor.preprocess_job(embedding_input)
            embedding_response = await embedding_client.create(preprocessed_description)
            job["embedding"] = embedding_response.data[0].embedding
            job.pop("meta_tags", None)
            doc_id = generate_job_id(job)
            await es_client.index_job(doc_id, job)
            logging.info(f"✅ Indexed job {job['site_id']} | {job['job_title']}")
            return job_id, None
        except Exception as e:
            logging.error(f"❌ Failed to process/index job {job.get('site_id')}: {e}")
            return None, job_id


async def process_and_index_new_jobs():
    """Process and index new jobs from ejobs.ro in parallel."""
    metadata = await es_client.get_metadata("last_ejobs")
    last_indexed_id = metadata.get("id")
    last_indexed_creation_date = metadata.get("creation_date")

    latest_job_id, latest_job_creation_date = await asyncio.to_thread(get_latest_job_id)
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

    newest_scraped_id = latest_job_id
    newest_scraped_creation_date = latest_job_creation_date

    MAX_DAILY_JOBS = 50
    job_ids = list(range(latest_job_id, last_indexed_id, -1))
    if len(job_ids) > MAX_DAILY_JOBS:
        logging.info(f"⚠️ Limiting job processing to {MAX_DAILY_JOBS} jobs")
        job_ids = job_ids[:MAX_DAILY_JOBS]
    logging.info(
        f"Scraping {len(job_ids)} jobs from ID {job_ids[0]} down to {job_ids[-1]}"
    )

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = [process_single_job(job_id, semaphore) for job_id in job_ids]

    results = await asyncio.gather(*tasks)

    await es_client.update_metadata(
        "last_ejobs",
        {"id": newest_scraped_id, "creation_date": newest_scraped_creation_date}
    )
    logging.info(f"✅ Updated metadata: last_ejobs = {newest_scraped_id}")


async def process_single_department_job(job_summary,semaphore):
    """Process and index a single job from a department."""
    async with semaphore:
        job_id = job_summary["id"]
        job = await asyncio.to_thread(process_job, job_id)
        if not job:
            logging.info(f"Skipping job {job_id}: not found or empty.")
            return None, job_id

        try:
            embedding_description = clean_html_for_embedding(job["description"])
            embedding_input = f"{job['job_title']}\n{embedding_description}\n{job['meta_tags']}"
            preprocessed_description = await text_preprocessor.preprocess_job(embedding_input)
            embedding_response = await embedding_client.create(preprocessed_description)
            job["embedding"] = embedding_response.data[0].embedding
            job.pop("meta_tags", None)
            doc_id = generate_job_id(job)
            await es_client.index_job(doc_id, job)
            logging.info(f"✅ Indexed job {job['site_id']} | {job['job_title']}")
            return job_id, None
        except Exception as e:
            logging.error(f"❌ Failed to index job {job.get('site_id')}: {e}")
            return None, job_id


async def process_and_index_jobs_from_department():
    """Process and index new jobs from a specific department in parallel."""
    metadata = await es_client.get_metadata("last_ejobs_dept57")
    last_indexed_id = metadata.get("id")
    last_indexed_creation_date = metadata.get("creation_date")

    if last_indexed_id is None:
        logging.warning(
            "⚠️ No last_ejobs_dept57_indexed_id found. Fetching last 300 jobs."
        )
        last_indexed_id = 0

    jobs = await asyncio.to_thread(fetch_new_jobs_from_department, DEPARTMENT_ID, last_indexed_creation_date, 300)
    logging.info(
        f"Total new jobs fetched for department {DEPARTMENT_ID}: {len(jobs)}"
    )

    if not jobs:
        logging.info("No new jobs to process.")
        return
    
    def parse_dt(job):
        return datetime.fromisoformat(job["creationDate"].replace("Z", "+00:00"))
    newest_job = max(jobs, key=parse_dt)
    newest_job_id = newest_job["id"]
    newest_job_creation_date = newest_job["creationDate"]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = [process_single_department_job(job_summary, semaphore) for job_summary in jobs]

    results = await asyncio.gather(*tasks)

    await es_client.update_metadata(
        "last_ejobs_dept57",
        {"id": newest_job_id, "creation_date": newest_job_creation_date
    })
    
    logging.info(
        f"✅ Updated metadata: last_ejobs_dept57 = {newest_job_id}, {newest_job_creation_date}"
    )

def main():
    parser = argparse.ArgumentParser(description="Job processing options")
    parser.add_argument(
        "--mode",
        choices=["all", "department", "both"],
        default="both",
        help="Which job processing to run: all (default), department, or both"
    )
    args = parser.parse_args()

    async def run_all():
        if args.mode == "all":
            await process_and_index_new_jobs()
        elif args.mode == "both":
            await process_and_index_new_jobs()
            await process_and_index_jobs_from_department()
        elif args.mode == "department":
            await process_and_index_jobs_from_department()
        
        await es_client.client.close()

    asyncio.run(run_all())

if __name__ == "__main__":
    main()