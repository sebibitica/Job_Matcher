import logging
from datetime import datetime
from ..clients.es_client import ElasticsearchClient

logging.basicConfig(level=logging.INFO)
es_client = ElasticsearchClient()

def remove_expired_jobs():
    """Delete jobs from Elasticsearch where expiration_date < today."""
    today = datetime.today().strftime("%Y-%m-%d")
    query = {
        "range": {
            "expiration_date": {"lt": today}
        }
    }
    
    logging.info(f"Removing expired jobs with expiration_date < {today}")
    result = es_client.client.delete_by_query(
        index="jobs",
        body={"query": query}
    )
    logging.info(f"Deleted {result['deleted']} expired jobs.")

if __name__ == "__main__":
    remove_expired_jobs()