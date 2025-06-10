from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
import os
import uuid
from typing import Optional
from ..types.types import *
import numpy as np
import heapq

class ElasticsearchClient:
    """
    Client for interacting with Elasticsearch to manage user profiles, jobs, applications,
    and perform job matching and search operations.
    """
    def __init__(self):
        self.client = AsyncElasticsearch(
            os.getenv('ELASTICSEARCH_URL'),
        )
    
    async def ensure_indices_exist(self):
        """Ensure all required indices exist with correct mappings."""
        indices = {
            "jobs": {
                "mappings": {
                    "properties": {
                        "company": {"type": "keyword"},
                        "date_uploaded": {"type": "date", "format": "strict_date_optional_time"},
                        "description": {"type": "text"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 1536,
                            "index": True,
                            "similarity": "cosine",
                            "index_options": {"type": "hnsw", "m": 32, "ef_construction": 100}
                        },
                        "expiration_date": {"type": "date", "format": "yyyy-MM-dd"},
                        "job_title": {"type": "text"},
                        "job_url": {"type": "keyword"},
                        "location": {
                            "properties": {
                                "city": {"type": "keyword"},
                                "country": {"type": "keyword"}
                            }
                        },
                        "site_id": {"type": "keyword"}
                    }
                }
            },
            "scraper_metadata": {
                "mappings": {
                    "properties": {
                        "creation_date": {"type": "date"},
                        "id": {"type": "long"}
                    }
                }
            },
            "user_applied_jobs": {
                "mappings": {
                    "properties": {
                        "applied_date": {"type": "date"},
                        "job_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"}
                    }
                }
            },
            "user_profiles": {
                "mappings": {
                    "properties": {
                        "date_created": {"type": "date"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 1536,
                            "index": True,
                            "similarity": "cosine",
                            "index_options": {"type": "int8_hnsw", "m": 16, "ef_construction": 100}
                        },
                        "structured_profile": {
                            "type": "object",
                            "enabled": False
                        },
                        "user_id": {"type": "keyword"}
                    }
                }
            }
        }

        for index, body in indices.items():
            exists = await self.client.indices.exists(index=index)
            if not exists:
                await self.client.indices.create(index=index, **body)

    # -------------------------------
    #     User Profile handling
    # -------------------------------

    async def index_user_profile(self, user_id: str, document: dict):
        """Index or update a user profile document."""
        return await self.client.index(
            index="user_profiles",
            id=user_id,
            document=document
        )
    
    async def search_user_profile(self, user_id: str):
        """Retrieve a user profile by user ID."""
        if not user_id:
            return None
        try:
            result = await self.client.get(index="user_profiles", id=user_id)
            return result["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving user profile: {str(e)}")
        
    async def get_user_embedding(self, user_id: str):
        """Get the embedding vector from a user's profile."""
        if not user_id:
            return None
        profile = await self.search_user_profile(user_id)
        if not profile:
            return None
        return profile.get("embedding")
    

    # -------------------------------
    #     Jobs handling
    # -------------------------------
    
    async def index_job(self, job_id, job_data):
        """Index or update a job document."""
        return await self.client.index(
            index="jobs",
            id=job_id,
            document=job_data
        )
    
    async def get_job(self, job_id: str)-> Optional[FullJob]:
        """Retrieve a job by ID, excluding its embedding."""
        try:
            result = await self.client.get(index="jobs", id=job_id, _source_excludes=["embedding"])
            result["_source"]["id"] = job_id
            return FullJob.model_validate(result["_source"])
        except NotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving job: {str(e)}")
        
    async def get_jobs_batch(self, job_ids: list)-> list[BaseJob]:
        """Get multiple jobs in a single query"""
        if not job_ids:
            return {"hits": {"hits": []}}
        
        source_fields = [f for f in BaseJob.model_fields.keys() if f != "id"]

        response = await self.client.search(
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
    
    async def get_jobs_countries(self):
        """Return a list of all distinct countries from job postings."""
        response = await self.client.search(
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

    async def get_jobs_cities(self, country: str):
        """Return a list of all distinct cities for a given country."""
        response = await self.client.search(
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

    async def index_applied_job(self, document: dict):
        """Index a new applied job for a user."""
        return await self.client.index(
            index="user_applied_jobs",
            id=str(uuid.uuid4()),
            document=document
        )
    
    async def delete_applied_job(self, application_id: str, user_id: str):
        """Delete an applied job if the user is authorized."""
        if not await self.verify_application_ownership(application_id, user_id):
            raise ValueError("Not authorized to delete this application")
        return await self.client.delete(
            index="user_applied_jobs",
            id=application_id
        )
    
    async def is_applied_job(self, user_id: str, job_id: str):
        """Check if a user has applied for a specific job"""
        response = await self.client.search(
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

    async def get_user_applications(self, user_id: str):
        """Retrieve applications sorted by applied_date"""
        return await self.client.search(
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
    
    async def verify_application_ownership(self, application_id: str, user_id: str):
        """Check if a given application belongs to the user."""
        response = await self.client.get(index="user_applied_jobs", id=application_id)
        return response['_source']['user_id'] == user_id
    
    async def get_enriched_applications(self, user_id: str) -> list[AppliedJob]:
        """Return user's applications with job data, removing stale applications."""
        applications = await self.get_user_applications(user_id)
        apps = [{
            "application_id": hit["_id"],
            **hit["_source"]
        } for hit in applications.get("hits", {}).get("hits", [])]

        if not apps:
            return []

        # Get job data for all applications
        job_ids = [app["job_id"] for app in apps]
        job_list = await self.get_jobs_batch(job_ids)
        job_map = {job.id: job for job in job_list}

        # Update statuses and prepare results
        results = []
        for app in apps:
            job = job_map.get(app["job_id"])
            if not job:
                # If job is not found(it was deleted), delete the application
                await self.delete_applied_job(app["application_id"], user_id)
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
    
    async def search_jobs_by_embedding(self, embedding, k=15, exclude_job_ids: list = None) -> list[MatchedJob]:
        """
        KNN Search for jobs most similar to a given user profile embedding,
        excluding the jobs the user has already applied to.
        """
        fetch_size = k + (len(exclude_job_ids) if exclude_job_ids else 0)
        
        exclude_job_ids = set(exclude_job_ids) if exclude_job_ids else set()

        source_fields = [f for f in MatchedJob.model_fields if f not in ("id", "score")]

        query_body = {
            "knn": {
                "field": "embedding",
                "query_vector": embedding,
                "k": fetch_size,
                "num_candidates": 100
            },
            "_source": source_fields,
            "size": fetch_size
        }

        response = await self.client.search(
            index="jobs",
            body=query_body
        )

        hits = response.get("hits", {}).get("hits", [])

        matched_jobs = []
        for hit in hits:
            if hit["_id"] in exclude_job_ids:
                continue
            source = hit["_source"]
            matched_job = MatchedJob.model_validate({
                "id": hit["_id"],
                "score": hit.get("_score", 0),
                **source
            })
            matched_jobs.append(matched_job)
            if len(matched_jobs) == k:
                break

        return matched_jobs
    
    # -------------------------------
    #     Job Search handling
    # -------------------------------
    async def search_jobs_by_keyword_with_similarity(self, request: SearchRequest, user_id: str) -> list[BaseJob]:
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

        user_embedding = await self.get_user_embedding(user_id)

        source_fields = [f for f in BaseJob.model_fields.keys() if f != "id"]
        if user_embedding:
            source_fields.append("embedding")

        response = await self.client.search(
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

    async def get_metadata(self, doc_id: str, index: str = "scraper_metadata") -> dict:
        """Retrieve webscraping metadata by document ID."""
        if await self.client.exists(index=index, id=doc_id):
            response = await self.client.get(index=index, id=doc_id)
            return response["_source"]
        return {}

    async def update_metadata(self, doc_id: str, data: dict, index: str = "scraper_metadata") -> None:
        """Update or insert webscraping metadata."""
        await self.client.index(index=index, id=doc_id, document=data)