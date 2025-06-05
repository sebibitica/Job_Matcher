from datetime import datetime, timezone
from ..cv_processor.cv_processor import CVProcessor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient
from ..preprocessor.preprocessor import TextPreprocessor

class ProfileManager:
    """Manage user profiles in Elasticsearch"""

    def __init__(self, embedding_client: OpenAIEmbeddingClient, es_client: ElasticsearchClient, preprocessor: TextPreprocessor):
        self.embedding_client = embedding_client
        self.es_client = es_client
        self.preprocessor = preprocessor

    async def set_user_profile_by_file(self, user_id: str, file_stream):
        """Set user profile, using embedding from a CV file."""
        embedding = await CVProcessor.process_file(file_stream, self.preprocessor, self.embedding_client)

        doc = {
            "user_id": user_id,
            "embedding": embedding,
            "date_created": datetime.now(timezone.utc).isoformat()
        }

        return await self.es_client.index_user_profile(user_id, doc)

    async def set_user_profile_by_text(self, user_id: str, profile_text: str):
        """Set user profile, using embedding from raw profile text."""
        preprocessed_profile = await self.preprocessor.preprocess_cv(profile_text)

        response_embedding = await self.embedding_client.create(preprocessed_profile)

        embedding = response_embedding.data[0].embedding

        doc = {
            "user_id": user_id,
            "embedding": embedding,
            "date_created": datetime.now(timezone.utc).isoformat()
        }

        return await self.es_client.index_user_profile(user_id, doc)

    async def get_user_profile(self, user_id: str):
        """Retrieve a user profile by user ID."""
        return await self.es_client.search_user_profile(user_id)
