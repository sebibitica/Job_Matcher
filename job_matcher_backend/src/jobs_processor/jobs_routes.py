from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from ..clients.firebase.verify_token import get_current_user
from ..dependencies.dependencies import get_es_client
from ..types.types import SearchRequest, BaseJob

router = APIRouter(
    prefix="/search_jobs",
    tags=["Job Search"]
)

@router.get("/countries")
async def get_countries(es_client = Depends(get_es_client)):
    countries = await es_client.get_jobs_countries()
    return countries

@router.get("/cities")
async def get_cities(country: str = Query(...), es_client = Depends(get_es_client)):
    cities = await es_client.get_jobs_cities(country)
    return cities

@router.get("/{job_id}")
async def get_job(
    job_id: str,
    es_client = Depends(get_es_client)
):
    try:
        job = await es_client.get_job(job_id)
        if not job:
            return JSONResponse(content={"error": "Job not found"}, status_code=404)
        return {"job": job}
    except Exception as e:
        return JSONResponse(content={"error": "Failed to retrieve job", "details": str(e)}, status_code=500)
    
@router.post("", response_model=list[BaseJob])
async def job_search(
    request: SearchRequest,
    user_id: str = Depends(get_current_user),
    es_client = Depends(get_es_client)
):
    try:
        return await es_client.search_jobs_by_keyword_with_similarity(request, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))