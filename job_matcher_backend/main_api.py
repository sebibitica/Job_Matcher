from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from io import BytesIO
from src.jobs_matcher.jobs_matcher import JobsMatcher
from src.applied_jobs.job_apply_storage_handler import JobApplyStorageHandler
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.firebase.verify_token import get_current_user
from src.interview import interview_routes
from src.user_profile import profile_routes
from src.clients.es_client import ElasticsearchClient
from src.types.types import *
from typing import List
import numpy as np
import heapq

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

jobs_matcher = JobsMatcher()
job_apply_storage_handler = JobApplyStorageHandler()
es_client = ElasticsearchClient()

@app.post("/apply_to_job/{job_id}")
async def apply_to_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    try:
        response = await job_apply_storage_handler.save_application(user_id, job_id)
        return {"message": "Job application saved successfully", "response": response}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@app.get("/applied_jobs")
async def get_applied_jobs(user_id: str = Depends(get_current_user)):
    try:
        applications = await job_apply_storage_handler.get_enriched_applications(user_id)
        if not applications:
            return JSONResponse(content={"error": "No applications found"}, status_code=404)
        apps = []
        for app in applications:
            app_data = AppliedJob(
                id=app["job_id"],
                job_title=app["job_data"]["job_title"],
                company=app["job_data"]["company"],
                location=app["job_data"]["location"],
                application_id=app["application_id"],
                applied_date=app["applied_date"],
            )
            apps.append(app_data)

        print(apps)

        return {"applications": apps}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@app.delete("/applied_jobs/{application_id}")
async def delete_applied_job(
    application_id: str,
    user_id: str = Depends(get_current_user)
):
    try:        
        await job_apply_storage_handler.delete_application(application_id, user_id)
        return {"message": "Application deleted successfully"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@app.get("/is_applied_job/{job_id}")
async def is_applied_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    try:
        response = await job_apply_storage_handler.is_applied_job(user_id, job_id)
        return {"is_applied": response}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@app.get("/jobs/{job_id}")
async def get_job(
    job_id: str
):
    try:
        job = es_client.get_job(job_id)
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        return {"job": job}
    except Exception as e:
        return JSONResponse(content={"error": "Failed to retrieve job", "details": str(e)}, status_code=500)
    
@app.get("/get_job_matches_by_profile")
async def get_job_matches_by_profile(
    user_id: str = Depends(get_current_user)
):
    try:
        results = jobs_matcher.get_matching_jobs_with_user_id(user_id)
        if not results:
            return JSONResponse(content={"error": "No matching jobs found"}, status_code=404)
        jobs=[]
        for hit in results['hits']['hits']:
            source = hit["_source"]
            job=MatchedJob(
                id=hit["_id"],
                job_title=source["job_title"],
                company=source["company"],
                location=source["location"],
                score=hit["_score"]
            )
            jobs.append(job)

        return {"message": "Job matching successful", "jobs": jobs}
    
    except Exception as e:
        return JSONResponse(content={"error": "Failed to match jobs", "details": str(e)}, status_code=500)

@app.post("/get_job_matches_logged_out")
async def get_job_matches_by_file_upload(file: UploadFile = File(...)):
    try:
        file_extension = file.filename.split(".")[-1].lower()
        file_bytes = BytesIO(await file.read())

        if file_extension not in ["docx", "pdf"]:
            return JSONResponse(
                content={"error": "Unsupported file type. Only DOCX and PDF are allowed."},
                status_code=400,
            )

        results = jobs_matcher.get_matching_jobs_by_file(file_bytes)
        if not results:
            return JSONResponse(content={"error": "No matching jobs found"}, status_code=404)
        jobs=[]
        for hit in results['hits']['hits']:
            source = hit["_source"]
            job=MatchedJob(
                id=hit["_id"],
                job_title=source["job_title"],
                company=source["company"],
                location=source["location"],
                score=hit["_score"]
            )
            jobs.append(job)

        return {"message": "Job matching successful", "jobs": jobs}

    except Exception as e:
        return JSONResponse(content={"error": "Failed to process file", "details": str(e)}, status_code=500)
    
@app.get("/get_countries")
async def get_countries():
    countries = es_client.get_jobs_countries()
    return countries

@app.get("/get_cities")
async def get_cities(country: str = Query(...)):
    cities = es_client.get_jobs_cities(country)
    return cities
    
@app.post("/job_search", response_model=List[BaseJob])
async def job_search(
    request: SearchRequest,
    user_id: str = Depends(get_current_user)
):
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

    try:
        if not must_clauses:
            query_body = {
                "bool": {
                    "filter": filter_clauses if filter_clauses else [],
                    "must": [{"match_all": {}}]
                }
            }
        else:
            query_body = {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            }

        keyword_response = es_client.client.search(
            index="jobs2",
            size=100,
            query=query_body,
            _source=["job_title", "company", "location", "embedding"]
        )

        hits = keyword_response["hits"]["hits"]

        if not hits:
            return []

        user_embedding = es_client.get_user_embedding(user_id)
        if not user_embedding:
            # No user embedding? Return top 15 keyword matches only
            return [
                BaseJob(id=hit["_id"], **hit["_source"])
                for hit in hits[:15]
            ]

        user_embedding_np = np.array(user_embedding)
        user_norm = np.linalg.norm(user_embedding_np)

        def cosine_similarity_np(vec):
            vec_np = np.array(vec)
            return np.dot(user_embedding_np, vec_np) / (user_norm * np.linalg.norm(vec_np) + 1e-10)

        ranked_hits = heapq.nlargest(
            15,
            hits,
            key=lambda hit: cosine_similarity_np(hit["_source"]["embedding"])
        )

        return [
            BaseJob(id=hit["_id"], **{k: v for k, v in hit["_source"].items() if k != "embedding"})
            for hit in ranked_hits[:15]
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
app.include_router(interview_routes.router)
app.include_router(profile_routes.router)

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
