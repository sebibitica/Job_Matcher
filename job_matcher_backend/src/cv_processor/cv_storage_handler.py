import uuid
from io import BytesIO
from datetime import datetime, timezone
from .cv_processor import CVProcessor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient

class CVStorageHandler:
    def __init__(self):
        self.embedding_client = OpenAIEmbeddingClient()
        self.es_client = ElasticsearchClient()

    async def save_resume(self, file_stream: BytesIO, user_id: str, filename: str):
        """Save resume to Elasticsearch with user association"""
        try:
            # Process CV to get embedding
            cv_processor = CVProcessor(file_stream, self.embedding_client)
            embedding = cv_processor.process()
            
            # Create resume document
            resume_id = str(uuid.uuid4())
            document = {
                "user_id": user_id,
                "filename": filename,
                "embedding": embedding,
                "upload_date": datetime.now(timezone.utc).isoformat(),
            }
            
            return self.es_client.index_resume(
                index="user_resumes",
                id=resume_id,
                document=document
            )
            
        except Exception as e:
            raise ValueError(f"Error saving resume: {str(e)}")
        
    async def delete_resume(self, resume_id: str, user_id: str):
        try:
            return self.es_client.delete_resume(resume_id, user_id)
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")
        
    async def get_user_resumes(self, user_id: str):
        try:
            return self.es_client.get_user_resumes(user_id)
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")
        