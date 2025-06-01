from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ..clients.firebase.verify_token import get_current_user
from .applied_jobs_manager import AppliedJobsManager

router = APIRouter(
    prefix="/applied_jobs",
    tags=["Applied Jobs"],
    dependencies=[Depends(get_current_user)]
)
applied_jobs_manager = AppliedJobsManager()

@router.post("/apply/{job_id}")
async def apply_to_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Apply the current user to a job."""
    try:
        response = await applied_jobs_manager.save_application(user_id, job_id)
        return {"message": "Job application saved successfully", "response": response}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@router.get("/")
async def get_applied_jobs(user_id: str = Depends(get_current_user)):
    """Retrieve all job applications for the current user."""
    try:
        applications = await applied_jobs_manager.get_enriched_applications(user_id)
        if not applications:
            return JSONResponse(content={"error": "No applications found"}, status_code=404)
        
        return {"applications": applications}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@router.delete("/{application_id}")
async def delete_applied_job(
    application_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a job application for the current user."""
    try:        
        await applied_jobs_manager.delete_application(application_id, user_id)
        return {"message": "Application deleted successfully"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
@router.get("/is_applied/{job_id}")
async def is_applied_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Check if the current user has applied to a specific job."""
    try:
        response = await applied_jobs_manager.is_applied_job(user_id, job_id)
        return {"is_applied": response}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )