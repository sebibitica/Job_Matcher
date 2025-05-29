from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from src.interview import interview_routes
from src.user_profile import profile_routes
from src.jobs_matcher import jobs_matcher_routes
from src.applied_jobs import applied_jobs_routes
from src.jobs_processor import jobs_routes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()

    # Get user token if it exists
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    token_preview = f"{token[:10]}..." if token else "No token"

    logger.info(
        f"Method: {request.method} | "
        f"Path: {request.url.path} | "
        f"Client: {request.client.host}:{request.client.port} | "
        f"Duration: {duration:.3f}s | "
        f"Status: {response.status_code} | "
        f"Token: {token_preview}"
    )
    
    return response

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