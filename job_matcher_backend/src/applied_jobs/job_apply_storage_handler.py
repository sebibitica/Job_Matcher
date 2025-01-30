# applied_jobs_handler.py
from datetime import datetime, timezone
from ..clients.es_client import ElasticsearchClient
import asyncio

class JobApplyStorageHandler:
    def __init__(self):
        self.es = ElasticsearchClient()
    
    async def save_application(self, user_id: str, job_id: str):
        document = {
            "user_id": user_id,
            "job_id": job_id,
            "applied_date": datetime.now(timezone.utc).isoformat(),
            "status": "active"
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
    handler = JobApplyStorageHandler()
    # app1 = await handler.save_application("user1", "job_1")
    # print(app1)
    # app2 = await handler.save_application("user1", "job_5")
    # print(app2)
    # app3 = await handler.save_application("user1", "job_11")
    # print(app3)
    # app4 = await handler.save_application("user2", "job_3")
    # print(app4)
    # app5 = await handler.save_application("user2", "job_7")
    # print(app5)

    #wait for the index to be updated
    await asyncio.sleep(3)
    print("Applications for user1:")
    final1 = await handler.get_enriched_applications("user1")
    print(final1)
    print("Applications for user2:")
    final2 = await handler.get_enriched_applications("user2")
    print(final2)

if __name__ == "__main__":
    asyncio.run(main())