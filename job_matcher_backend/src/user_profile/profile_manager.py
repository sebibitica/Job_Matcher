from datetime import datetime, timezone
from ..cv_processor.cv_processor import CVProcessor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient
from ..preprocessor.preprocessor import TextPreprocessor

class ProfileManager:
    def __init__(self):
        self.embedding_client = OpenAIEmbeddingClient()
        self.es_client = ElasticsearchClient()
        self.preprocessor = TextPreprocessor()

    async def set_user_profile_by_file(self, user_id: str, file_stream):
        embedding = CVProcessor.process_file(file_stream, self.preprocessor, self.embedding_client)

        doc = {
            "user_id": user_id,
            "embedding": embedding,
            "date_created": datetime.now(timezone.utc).isoformat()
        }

        return self.es_client.index_user_profile(user_id, doc)

    async def set_user_profile_by_text(self, user_id: str, profile_text: str):
        preprocessed_profile = self.preprocessor.preprocess_cv(profile_text)

        embedding = self.embedding_client.create(preprocessed_profile).data[0].embedding

        doc = {
            "user_id": user_id,
            "embedding": embedding,
            "date_created": datetime.now(timezone.utc).isoformat()
        }

        return self.es_client.index_user_profile(user_id, doc)

    def get_user_profile(self, user_id: str):
        return self.es_client.search_user_profile(user_id)
