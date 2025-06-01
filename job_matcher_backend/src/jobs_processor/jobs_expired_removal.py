import logging
from datetime import datetime
from ..clients.es_client import ElasticsearchClient
import asyncio

logging.basicConfig(level=logging.INFO)
es_client = ElasticsearchClient()

async def remove_expired_jobs():
    """Delete jobs from Elasticsearch where expiration_date < today."""
    today = datetime.today().strftime("%Y-%m-%d")
    query = {
        "range": {
            "expiration_date": {"lt": today}
        }
    }
    
    logging.info(f"Removing expired jobs with expiration_date < {today}")
    result = await es_client.client.delete_by_query(
        index="jobs",
        body={"query": query}
    )
    logging.info(f"Deleted {result['deleted']} expired jobs.")

    await es_client.client.close()

if __name__ == "__main__":
    asyncio.run(remove_expired_jobs())