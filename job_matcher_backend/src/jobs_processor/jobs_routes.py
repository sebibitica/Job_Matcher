from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from ..clients.firebase.verify_token import get_current_user
from ..clients.es_client import ElasticsearchClient
from ..types.types import SearchRequest, BaseJob


router = APIRouter()
es_client = ElasticsearchClient()

@router.get("/jobs/{job_id}")
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
    
@router.get("/get_countries")
async def get_countries():
    countries = es_client.get_jobs_countries()
    return countries

@router.get("/get_cities")
async def get_cities(country: str = Query(...)):
    cities = es_client.get_jobs_cities(country)
    return cities
    
@router.post("/job_search", response_model=list[BaseJob])
async def job_search(
    request: SearchRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        return es_client.search_jobs_by_keyword_with_similarity(request, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))