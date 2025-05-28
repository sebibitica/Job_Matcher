# applied_jobs_handler.py
from datetime import datetime, timezone
from ..clients.es_client import ElasticsearchClient
import asyncio

class AppliedJobsManager:
    def __init__(self):
        self.es = ElasticsearchClient()
    
    async def save_application(self, user_id: str, job_id: str):
        document = {
            "user_id": user_id,
            "job_id": job_id,
            "applied_date": datetime.now(timezone.utc).isoformat(),
        }
        return self.es.index_applied_job(document)
    
    async def get_enriched_applications(self, user_id: str):
        applications = self.es.get_enriched_applications(user_id)
        return applications
    
    async def delete_application(self, application_id: str, user_id: str):
        return self.es.delete_applied_job(application_id, user_id)
    
    async def is_applied_job(self, user_id: str, job_id: str):
        return self.es.is_applied_job(user_id, job_id)


async def main():
    handler = AppliedJobsManager()
    user_id = "A81eScgtsdbAKIhVzUtXclWk7A02"
    job_id = "jobs_matcher_1"
    # Save an application
    response = await handler.save_application(user_id, job_id)
    print(f"Application saved: {response}")
    # Get enriched applications
    applications = await handler.get_enriched_applications(user_id)
    print(f"Enriched applications: {applications}")

if __name__ == "__main__":
    asyncio.run(main())