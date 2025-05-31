from fastapi import UploadFile, File, Depends, APIRouter
from fastapi.responses import JSONResponse
from io import BytesIO
from .jobs_matcher import JobsMatcher
from ..clients.firebase.verify_token import get_current_user

router = APIRouter()
jobs_matcher = JobsMatcher()

@router.get("/get_job_matches_by_profile")
async def get_job_matches_by_profile(
    user_id: str = Depends(get_current_user)
):
    """Get matching jobs for the current user's profile."""
    try:
        matched_jobs = jobs_matcher.get_matching_jobs_with_user_id(user_id)
        if not matched_jobs:
            return JSONResponse(content={"error": "No matching jobs found"}, status_code=404)
        return {
            "message": "Job matching successful",
            "jobs": [job.model_dump() for job in matched_jobs]
        }
    
    except Exception as e:
        return JSONResponse(content={"error": "Failed to match jobs", "details": str(e)}, status_code=500)

@router.post("/get_job_matches_logged_out")
async def get_job_matches_by_file_upload(file: UploadFile = File(...)):
    """Get matching jobs by uploading a CV file (for logged-out users)."""
    try:
        file_extension = file.filename.split(".")[-1].lower()
        file_bytes = BytesIO(await file.read())

        if file_extension not in ["docx", "pdf"]:
            return JSONResponse(
                content={"error": "Unsupported file type. Only DOCX and PDF are allowed."},
                status_code=400,
            )

        matched_jobs = jobs_matcher.get_matching_jobs_by_file(file_bytes)
        if not matched_jobs:
            return JSONResponse(content={"error": "No matching jobs found"}, status_code=404)

        return {
            "message": "Job matching successful",
            "jobs": [job.model_dump() for job in matched_jobs]
        }

    except Exception as e:
        return JSONResponse(content={"error": "Failed to process file", "details": str(e)}, status_code=500)