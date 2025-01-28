from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from io import BytesIO
from src.jobs_matcher.jobs_matcher import JobsMatcher
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_job_matches")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_extension = file.filename.split(".")[-1].lower()
        file_bytes = BytesIO(await file.read())

        if file_extension not in ["docx", "pdf"]:
            return JSONResponse(
                content={"error": "Unsupported file type. Only DOCX and PDF are allowed."},
                status_code=400,
            )

        # Use JobsMatcher to process the uploaded file and find matching jobs
        matcher = JobsMatcher(file_stream=file_bytes)
        matcher.process_cv()
        results = matcher.find_matching_jobs(top_k=10)

        return {"message": "Job matching successful", "results": results['hits']['hits']}

    except Exception as e:
        return JSONResponse(content={"error": "Failed to process file", "details": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
