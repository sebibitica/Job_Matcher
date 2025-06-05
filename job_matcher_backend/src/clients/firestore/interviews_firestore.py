from datetime import datetime
import uuid
from .firestore_client import FirestoreClient

class InterviewsManager(FirestoreClient):
    """
    Manages interview sessions for users in Firestore.
    Provides methods to create, update, retrieve, and delete interviews.
    """
    async def create_interview(self, user_id: str, job_id: str, job_title: str, messages: list) -> str:
        """Create a new interview and return unique interview_id"""
        interview_id = str(uuid.uuid4())
        doc_ref = self.client.collection("users").document(user_id)\
                    .collection("interviews").document(interview_id)
        
        await doc_ref.set({
            "job_id": job_id,
            "job_title": job_title,
            "messages": messages,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        })
        return interview_id

    async def save_messages(self, user_id: str, interview_id: str, messages: list):
        """Update the messages and last_updated timestamp for an interview."""
        doc_ref = self.client.collection("users").document(user_id)\
                    .collection("interviews").document(interview_id)
        
        await doc_ref.update({
            "messages": messages,
            "last_updated": datetime.utcnow()
        })

    async def load_messages(self, user_id: str, interview_id: str) -> list:
        """Retrieve the messages for a specific interview."""
        doc_ref = self.client.collection("users").document(user_id)\
                    .collection("interviews").document(interview_id)
        
        doc = await doc_ref.get()
        if doc.exists:
            messages = doc.to_dict().get("messages", [])
            return messages

    async def get_user_interviews(self, user_id: str) -> list:
        """Get all interviews for a user"""
        col_ref = self.client.collection("users").document(user_id)\
                    .collection("interviews")
        
        docs = col_ref.stream()
        return [{
                    "id": doc.id,
                    "title": doc.to_dict().get("job_title"),
                    "job_id": doc.to_dict().get("job_id"),
                    "last_updated": doc.to_dict().get('last_updated').isoformat(),
                 } async for doc in docs]
    
    async def delete_interview(self, user_id: str, interview_id: str):
        """Permanently delete an interview session"""
        doc_ref = self.client.collection("users").document(user_id)\
                    .collection("interviews").document(interview_id)
        await doc_ref.delete()