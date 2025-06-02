# applied_jobs_handler.py
from datetime import datetime, timezone
from ..clients.es_client import ElasticsearchClient

class AppliedJobsManager:
    """
    Handles saving, retrieving, and deleting job applications for users.
    """
    def __init__(self):
        self.es = ElasticsearchClient()
    
    async def save_application(self, user_id: str, job_id: str):
        """Save a new job application for a user."""
        if await self.is_applied_job(user_id, job_id):
            raise ValueError("User has already applied to this job.")
        
        document = {
            "user_id": user_id,
            "job_id": job_id,
            "applied_date": datetime.now(timezone.utc).isoformat(),
        }
        return await self.es.index_applied_job(document)
    
    async def get_enriched_applications(self, user_id: str):
        """Retrieve all applications for a user, enriched with job data.""" 
        return await self.es.get_enriched_applications(user_id)
    
    async def delete_application(self, application_id: str, user_id: str):
        """Delete a user's job application."""
        return await self.es.delete_applied_job(application_id, user_id)
    
    async def is_applied_job(self, user_id: str, job_id: str):
        """Check if a user has applied to a specific job."""
        return await self.es.is_applied_job(user_id, job_id)