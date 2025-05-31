from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from dotenv import load_dotenv
import os
import uuid
from typing import Optional
from ..types.types import *
import numpy as np
import heapq

load_dotenv()

class ElasticsearchClient:
    """
    Client for interacting with Elasticsearch to manage user profiles, jobs, applications,
    and perform job matching and search operations.
    """
    def __init__(self):
        self.client = Elasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
        )

    # -------------------------------
    #     User Profile handling
    # -------------------------------

    def index_user_profile(self, user_id: str, document: dict):
        """Index or update a user profile document."""
        return self.client.index(
            index="user_profiles",
            id=user_id,
            document=document
        )
    
    def search_user_profile(self, user_id: str):
        """Retrieve a user profile by user ID."""
        if not user_id:
            return None
        try:
            result = self.client.get(index="user_profiles", id=user_id)
            return result["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving user profile: {str(e)}")
        
    def get_user_embedding(self, user_id: str):
        """Get the embedding vector from a user's profile."""
        if not user_id:
            return None
        profile = self.search_user_profile(user_id)
        if not profile:
            return None
        return profile.get("embedding")
    

    # -------------------------------
    #     Jobs handling
    # -------------------------------
    
    def index_job(self, job_id, job_data):
        """Index or update a job document."""
        return self.client.index(
            index="jobs",
            id=job_id,
            document=job_data
        )
    
    def get_job(self, job_id: str)-> Optional[FullJob]:
        """Retrieve a job by ID, excluding its embedding."""
        try:
            result = self.client.get(index="jobs", id=job_id, _source_excludes=["embedding"])
            result["_source"]["id"] = job_id
            return FullJob.model_validate(result["_source"])
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving job: {str(e)}")
        
    def get_jobs_batch(self, job_ids: list)-> list[BaseJob]:
        """Get multiple jobs in a single query"""
        if not job_ids:
            return {"hits": {"hits": []}}
        
        source_fields = [f for f in BaseJob.model_fields.keys() if f != "id"]

        response = self.client.search(
            index="jobs",
            body={
                "query": {"terms": {"_id": job_ids}},
                "_source": source_fields,
                "size": len(job_ids)
            }
        )

        hits = response.get("hits", {}).get("hits", [])
        jobs = []
        for hit in hits:
            job_data = {
                "id": hit["_id"],
                **hit["_source"]
            }
            jobs.append(BaseJob.model_validate(job_data))

        return jobs
    
    def get_jobs_countries(self):
        """Return a list of all distinct countries from job postings."""
        response = self.client.search(
            index="jobs",
            size=0,
            aggs={
                "distinct_countries": {
                    "terms": {
                        "field": "location.country",
                        "size": 1000
                    }
                }
            }
        )
        countries = [bucket['key'] for bucket in response['aggregations']['distinct_countries']['buckets']]
        return countries

    def get_jobs_cities(self, country: str):
        """Return a list of all distinct cities for a given country."""
        response = self.client.search(
            index="jobs",
            size=0,
            query={"term": {"location.country": country}},
            aggs={
                "distinct_cities": {
                    "terms": {
                        "field": "location.city",
                        "size": 1000
                    }
                }
            }
        )
        cities = [bucket['key'] for bucket in response['aggregations']['distinct_cities']['buckets']]
        return cities
    

    # -------------------------------
    #     Applied Jobs handling 
    # -------------------------------

    def index_applied_job(self, document: dict):
        """Index a new applied job for a user."""
        return self.client.index(
            index="user_applied_jobs",
            id=str(uuid.uuid4()),
            document=document
        )
    
    def delete_applied_job(self, application_id: str, user_id: str):
        """Delete an applied job if the user is authorized."""
        if not self.verify_application_ownership(application_id, user_id):
            raise ValueError("Not authorized to delete this application")
        return self.client.delete(
            index="user_applied_jobs",
            id=application_id
        )
    
    def is_applied_job(self, user_id: str, job_id: str):
        """Check if a user has applied for a specific job"""
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

    def get_user_applications(self, user_id: str):
        """Retrieve applications sorted by applied_date"""
        return self.client.search(
            index="user_applied_jobs",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}}
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
    
    def verify_application_ownership(self, application_id: str, user_id: str):
        """Check if a given application belongs to the user."""
        response = self.client.get(index="user_applied_jobs", id=application_id)
        return response['_source']['user_id'] == user_id
    
    def get_enriched_applications(self, user_id: str) -> list[AppliedJob]:
        """Return user's applications with job data, removing stale applications."""
        applications = self.get_user_applications(user_id)
        apps = [{
            "application_id": hit["_id"],
            **hit["_source"]
        } for hit in applications.get("hits", {}).get("hits", [])]

        if not apps:
            return []

        # Get job data for all applications
        job_ids = [app["job_id"] for app in apps]
        job_list = self.get_jobs_batch(job_ids)
        job_map = {job.id: job for job in job_list}

        # Update statuses and prepare results
        results = []
        for app in apps:
            job = job_map.get(app["job_id"])
            if not job:
                # If job is not found(it was deleted), delete the application
                self.delete_applied_job(app["application_id"], user_id)
            else:
                # Add job data to AppliedJob model result
                applied_job = AppliedJob.model_validate({
                    **job.model_dump(),
                    "application_id": app["application_id"],
                    "applied_date": app["applied_date"],
                })
                results.append(applied_job)

        return results
    

    # -------------------------------
    #   Job Match KNN handling
    # -------------------------------
    
    def search_jobs_by_embedding(self, embedding, k=15, exclude_job_ids: list = None) -> list[MatchedJob]:
        """
        KNN Search for jobs most similar to a given user profile embedding,
        excluding the jobs the user has already applied to.
        """
        if exclude_job_ids:
            k=k+len(exclude_job_ids)
        
        source_fields = [f for f in MatchedJob.model_fields if f not in ("id", "score")]

        query_body = {
            "knn": {
                "field": "embedding",
                "query_vector": embedding,
                "k": k,
                "num_candidates": 100
            },
            "_source": source_fields,
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

        response = self.client.search(
            index="jobs",
            body=query_body
        )

        hits = response.get("hits", {}).get("hits", [])

        matched_jobs = []
        for hit in hits:
            source = hit["_source"]
            matched_job = MatchedJob.model_validate({
                "id": hit["_id"],
                "score": hit.get("_score", 0),
                **source
            })
            matched_jobs.append(matched_job)

        return matched_jobs
    
    # -------------------------------
    #     Job Search handling
    # -------------------------------
    def search_jobs_by_keyword_with_similarity(self, request: SearchRequest, user_id: str) -> list[BaseJob]:
        """
        Search jobs by keyword and location,
        ranking by similarity to user's embedding if available.
        """
        must_clauses = []
        filter_clauses = []

        if request.query and request.query.strip():
            must_clauses.append({
                "match_phrase_prefix": {
                    "job_title": {
                        "query": request.query
                    }
                }
            })

        if request.location:
            if request.location.city:
                filter_clauses.append({"term": {"location.city": request.location.city}})
            if request.location.country:
                filter_clauses.append({"term": {"location.country": request.location.country}})

        query_body = {
            "bool": {
                "must": must_clauses if must_clauses else [{"match_all": {}}],
                "filter": filter_clauses
            }
        }

        user_embedding = self.get_user_embedding(user_id)

        source_fields = [f for f in BaseJob.model_fields.keys() if f != "id"]
        if user_embedding:
            source_fields.append("embedding")

        response = self.client.search(
            index="jobs",
            size=100,
            query=query_body,
            _source=source_fields
        )

        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return []
        
        if not user_embedding:
            # No embedding: return keyword matches only
            return [BaseJob(id=hit["_id"], **hit["_source"]) for hit in hits[:15]]

        user_embedding_np = np.array(user_embedding)
        user_norm = np.linalg.norm(user_embedding_np)

        def cosine_similarity(vec):
            vec_np = np.array(vec)
            return np.dot(user_embedding_np, vec_np) / (user_norm * np.linalg.norm(vec_np) + 1e-10)

        # use a heap to get the top 15 jobs based on cosine similarity
        top_hits = heapq.nlargest(
            15,
            hits,
            key=lambda hit: cosine_similarity(hit["_source"]["embedding"])
        )

        return [
            BaseJob(id=hit["_id"], **{k: v for k, v in hit["_source"].items() if k != "embedding"})
            for hit in top_hits
        ]


    # ----------------------------------
    #  Webscraping Metadata handling
    # ----------------------------------

    def get_metadata(self, doc_id: str, index: str = "scraper_metadata") -> dict:
        """Retrieve webscraping metadata by document ID."""
        if self.client.exists(index=index, id=doc_id):
            return self.client.get(index=index, id=doc_id)["_source"]
        return {}

    def update_metadata(self, doc_id: str, data: dict, index: str = "scraper_metadata") -> None:
        """Update or insert webscraping metadata."""
        self.client.index(index=index, id=doc_id, document=data)