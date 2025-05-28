import os
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
es = Elasticsearch(ES_URL)

SOURCE_INDEX = "jobs2"
DEST_INDEX = "jobs"

def get_all_jobs(index):
    """Generator to scroll all jobs from the source index."""
    resp = es.search(
        index=index,
        scroll="2m",
        body={
            "size": 1000,
            "query": {
                "prefix": {
                    "site_id": "jobs_matcher_"
                }
            }
        }
    )
    scroll_id = resp['_scroll_id']
    hits = resp['hits']['hits']
    while hits:
        for doc in hits:
            yield doc
        resp = es.scroll(scroll_id=scroll_id, scroll="2m")
        scroll_id = resp['_scroll_id']
        hits = resp['hits']['hits']

def migrate_jobs():
    one_week_ago = (datetime.utcnow() - timedelta(weeks=1)).isoformat() + "Z"
    six_months_from_now = (datetime.utcnow() + timedelta(days=182)).strftime("%Y-%m-%d")
    actions = []
    for doc in get_all_jobs(SOURCE_INDEX):
        job = doc['_source']
        job['date_uploaded'] = one_week_ago
        job['expiration_date'] = six_months_from_now
        actions.append({
            "_index": DEST_INDEX,
            "_id": doc['_id'],
            "_source": job
        })
        if len(actions) >= 500:
            helpers.bulk(es, actions)
            actions = []
    if actions:
        helpers.bulk(es, actions)
    print("Migration complete.")

if __name__ == "__main__":
    migrate_jobs()