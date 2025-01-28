from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

class ElasticsearchClient:
    def __init__(self):
        self.client = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
        )
    
    def index_job(self, job_id, job_data):
        return self.client.index(
            index="jobs",
            id=job_id,
            document=job_data
        )
    
    def search_jobs_by_embedding(self, embedding, k=10):
        return self.client.search(
            index="jobs",
            body={
                "knn": {
                    "field": "embedding",
                    "query_vector": embedding,
                    "k": k,
                    "num_candidates": 100
                },
                "_source": ["job_title", "company", "location"],
                "size": k
            }
        )

if __name__ == "__main__":
    es = ElasticsearchClient()
    test_response = es.search_jobs_by_embedding([0.0]*1536)  # Test with dummy embedding
    print(test_response)