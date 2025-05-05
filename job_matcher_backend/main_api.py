from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from io import BytesIO
from src.jobs_matcher.jobs_matcher import JobsMatcher
# from src.cv_processor.cv_storage_handler import CVStorageHandler
from src.applied_jobs.job_apply_storage_handler import JobApplyStorageHandler
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.firebase.verify_token import get_current_user
from src.interview import interview_routes
from src.user_profile import profile_routes

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
# cv_storage_handler = CVStorageHandler()
job_apply_storage_handler = JobApplyStorageHandler()

# @app.post("/upload_resume")
# async def upload_resume(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
#     try:
#         file_extension = file.filename.split(".")[-1].lower()
#         if file_extension not in ["docx", "pdf"]:
#             return JSONResponse(
#                 content={"error": "Unsupported file type. Only DOCX and PDF are allowed."},
#                 status_code=400,
#             )

#         file_stream = BytesIO(await file.read())

#         response = await cv_storage_handler.save_resume(file_stream, user_id, file.filename)

#         return {"message": "Resume uploaded successfully", "response": response}

#     except Exception as e:
#         return JSONResponse(content={"error": "Failed to upload resume", "details": str(e)}, status_code=500)

# @app.get("/get_saved_resumes")
# async def get_saved_resumes(user_id: str = Depends(get_current_user)):
#     try:
#         response = await cv_storage_handler.get_user_resumes(user_id)
#         return {"message": "Resumes retrieved successfully", "response": response['hits']['hits']}
    
#     except Exception as e:
#         return JSONResponse(
#             content={"error": f"Failed to retrieve resumes: {str(e)}"},
#             status_code=500
#         )

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
        return {"applications": applications}
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

# @app.delete("/delete_resume/{resume_id}")
# async def delete_resume(
#     resume_id: str,
#     user_id: str = Depends(get_current_user)
# ):
#     try:
#         response = await cv_storage_handler.delete_resume(resume_id, user_id)
#         return {"message": "Resume deleted successfully"}
    
#     except Exception as e:
#         return JSONResponse(
#             content={"error": f"Failed to delete resume: {str(e)}"},
#             status_code=500
#         )
    
@app.get("/get_job_matches_by_profile")
async def get_job_matches_by_profile(
    user_id: str = Depends(get_current_user)
):
    try:
        results = jobs_matcher.get_matching_jobs_with_user_id(user_id)
        return {"message": "Job matching successful", "results": results['hits']['hits']}
    
    except Exception as e:
        return JSONResponse(content={"error": "Failed to match jobs", "details": str(e)}, status_code=500)

# @app.get("/get_job_matches_by_resume/{resume_id}")
# async def get_job_matches_by_resume(
#     resume_id: str,
#     user_id: str = Depends(get_current_user)
# ):
#     try:
#         results = jobs_matcher.get_matching_jobs_with_resume_id(resume_id, user_id)
#         return {"message": "Job matching successful", "results": results['hits']['hits']}
    
#     except Exception as e:
#         return JSONResponse(content={"error": "Failed to match jobs", "details": str(e)}, status_code=500)

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

        return {"message": "Job matching successful", "results": results['hits']['hits']}

    except Exception as e:
        return JSONResponse(content={"error": "Failed to process file", "details": str(e)}, status_code=500)
    
app.include_router(interview_routes.router)
app.include_router(profile_routes.router)

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
