from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

class ElasticsearchClient:
    def __init__(self):
        self.client = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
        )
        self.create_applied_jobs_index()
    
    def index_job(self, job_id, job_data):
        return self.client.index(
            index="jobs",
            id=job_id,
            document=job_data
        )
    
    def index_resume(self, index: str, id: str, document: dict):
        return self.client.index(index=index, id=id, document=document)
    
    
    def get_user_resumes(self, user_id: str):
        return self.client.search(
            index="user_resumes",
            body={
                "query": {
                    "term": {"user_id": user_id}
                },
                "_source": ["user_id", "filename", "upload_date"],
            }
        )
    
    def index_applied_job(self, document: dict):
        return self.client.index(
            index="user_applied_jobs",
            id=str(uuid.uuid4()),
            document=document
        )

    def get_user_applications(self, user_id: str):
        """Retrieve applications with active status only"""
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
                "_source": ["job_id", "applied_date"]
            }
        )
    
    def get_jobs_batch(self, job_ids: list):
        """Get multiple jobs in a single query"""
        return self.client.search(
            index="jobs",
            body={
                "query": {"terms": {"_id": job_ids}},
                "_source": ["job_title", "company", "location", "description", "job_url"],
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


    def verify_resume_ownership(self, resume_id: str, user_id: str):
        resume = self.client.get(index="user_resumes", id=resume_id)
        return resume['_source']['user_id'] == user_id
    
    def get_resume_embedding(self, resume_id: str, user_id: str):
        if not self.verify_resume_ownership(resume_id, user_id):
            raise ValueError("Not authorized to access this resume")
        response = self.client.get(index="user_resumes", id=resume_id)
        return response['_source']['embedding']
    
    def delete_resume(self, resume_id: str, user_id: str):
        if not self.verify_resume_ownership(resume_id, user_id):
            raise ValueError("Not authorized to delete this resume")
        return self.client.delete(index="user_resumes", id=resume_id)
    
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

    def create_applied_jobs_index(self):
        if not self.client.indices.exists(index="user_applied_jobs"):
            self.client.indices.create(
                index="user_applied_jobs",
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "job_id": {"type": "keyword"},
                            "applied_date": {"type": "date"},
                            "status": {"type": "keyword"}
                        }
                    }
                }
            )


if __name__ == "__main__":
    es = ElasticsearchClient()
    test_response = es.search_jobs_by_embedding([0.0]*1536)  # Test with dummy embedding
    print(test_response)