from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.interview import interview_routes
from src.user_profile import profile_routes
from src.jobs_matcher import jobs_matcher_routes
from src.applied_jobs import applied_jobs_routes
from src.jobs_processor import jobs_routes

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
    
app.include_router(interview_routes.router)
app.include_router(profile_routes.router)
app.include_router(jobs_matcher_routes.router)
app.include_router(applied_jobs_routes.router)
app.include_router(jobs_routes.router)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
