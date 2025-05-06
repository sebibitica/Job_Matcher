from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

class ElasticsearchClient:
    def __init__(self):
        self.client = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
        )

    
    def index_user_profile(self, user_id: str, document: dict):
        return self.client.index(
            index="user_profiles",
            id=user_id,
            document=document
        )
    
    def search_user_profile(self, user_id: str):
        try:
            result = self.client.get(index="user_profiles", id=user_id)
            return result["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving user profile: {str(e)}")
    
    def index_job(self, job_id, job_data):
        return self.client.index(
            index="jobs",
            id=job_id,
            document=job_data
        )
    
    def get_job(self, job_id: str):
        try:
            result = self.client.get(index="jobs", id=job_id, _source_excludes=["embedding"])
            result["_source"]["id"] = job_id
            return result["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving job: {str(e)}")
    
    def index_applied_job(self, document: dict):
        return self.client.index(
            index="user_applied_jobs",
            id=str(uuid.uuid4()),
            document=document
        )

    def get_user_applications(self, user_id: str):
        """Retrieve applications with active status only, sorted by applied_date"""
        return self.client.search(
            index="user_applied_jobs",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}},
                            {"term": {"status": "active"}}
                        ]
                    }
                },
                "size": 1000,
                "_source": ["job_id", "applied_date"],
                "sort": [
                    {"applied_date": {"order": "desc"}}
                ]
            }
        )
    
    def get_jobs_batch(self, job_ids: list):
        """Get multiple jobs in a single query"""
        return self.client.search(
            index="jobs",
            body={
                "query": {"terms": {"_id": job_ids}},
                "_source": ["job_title", "company", "location"],
                "size": len(job_ids)
            }
        )
    
    def get_enriched_applications(self, user_id: str):
        """Combined operation that returns active applications with job data"""
        applications = self.get_user_applications(user_id)
        apps = [{
            "application_id": hit["_id"],
            **hit["_source"]
        } for hit in applications["hits"]["hits"]]

        if not apps:
            return []

        # Get current job data
        job_ids = [app["job_id"] for app in apps]
        jobs_response = self.get_jobs_batch(job_ids)
        job_map = {hit["_id"]: hit["_source"] for hit in jobs_response["hits"]["hits"]}

        # Update statuses and prepare results
        results = []
        for app in apps:
            if app["job_id"] not in job_map:
                # Mark as archived in index
                self.delete_applied_job(app["application_id"], user_id)
            else:
                # Add job data to result
                results.append({
                    **app,
                    "job_data": job_map[app["job_id"]]
                })

        return results
    
    def is_applied_job(self, user_id: str, job_id: str):
        response = self.client.search(
            index="user_applied_jobs",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}},
                            {"term": {"job_id": job_id}},
                        ]
                    }
                }
            }
        )
        return response["hits"]["total"]["value"] > 0
    
    def verify_application_ownership(self, application_id: str, user_id: str):
        response = self.client.get(index="user_applied_jobs", id=application_id)
        return response['_source']['user_id'] == user_id
    
    def get_user_embedding(self, user_id: str):
        profile = self.search_user_profile(user_id)
        if not profile:
            return None
        return profile.get("embedding")
    
    def delete_applied_job(self, application_id: str, user_id: str):
        if not self.verify_application_ownership(application_id, user_id):
            raise ValueError("Not authorized to delete this application")
        return self.client.delete(
            index="user_applied_jobs",
            id=application_id
        )
    
    def search_jobs_by_embedding(self, embedding, k=10, exclude_job_ids: list = None):
        if exclude_job_ids:
            k=k+len(exclude_job_ids)
        
        query_body = {
            "knn": {
                "field": "embedding",
                "query_vector": embedding,
                "k": k,
                "num_candidates": 100
            },
            "_source": ["job_title", "company", "location", "description", "job_url"],
            "size": k
        }

        if exclude_job_ids:
            query_body["post_filter"] = {
                "bool": {
                    "must_not": [
                        {"terms": {"_id": exclude_job_ids}}
                    ]
                }
            }

        return self.client.search(
            index="jobs",
            body=query_body
        )


if __name__ == "__main__":
    es = ElasticsearchClient()
    test_response = es.search_jobs_by_embedding([0.0]*1536)  # Test with dummy embedding
    print(test_response)