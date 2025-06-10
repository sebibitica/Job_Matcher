from datetime import datetime, timezone
from ..cv_processor.cv_processor import CVProcessor
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient
from ..preprocessor.preprocessor import TextPreprocessor
from .profile_structurer.profile_structurer import ProfileStructurer

class ProfileManager:
    """Manage user profiles in Elasticsearch"""

    def __init__(self, embedding_client: OpenAIEmbeddingClient, es_client: ElasticsearchClient, preprocessor: TextPreprocessor, profile_structurer: ProfileStructurer):
        self.embedding_client = embedding_client
        self.es_client = es_client
        self.preprocessor = preprocessor
        self.profile_structurer = profile_structurer

    async def set_user_profile_by_file(self, user_id: str, file_stream):
        """Set user profile, using embedding from a CV file."""
        embedding, structured_profile = await CVProcessor.process_file_with_structure(file_stream, self.preprocessor, self.embedding_client, self.profile_structurer)

        doc = {
            "user_id": user_id,
            "embedding": embedding,
            "date_created": datetime.now(timezone.utc).isoformat(),
            "structured_profile": structured_profile
        }

        return await self.es_client.index_user_profile(user_id, doc)

    async def set_user_profile_by_text(self, user_id: str, structured_data: dict):
        """
        Set user profile from structured data from manual form entry.
        Converts structured data to text for embedding.
        """
        try:
            profile_text = await self._create_text_from_structured_data(structured_data)
            
            preprocessed_profile = await self.preprocessor.preprocess_cv(profile_text)
            response_embedding = await self.embedding_client.create(preprocessed_profile)
            embedding = response_embedding.data[0].embedding

            doc = {
                "user_id": user_id,
                "embedding": embedding,
                "date_created": datetime.now(timezone.utc).isoformat(),
                "structured_profile": structured_data
            }

            return await self.es_client.index_user_profile(user_id, doc)
        except Exception as e:
            raise Exception(f"Failed to set user profile from structured data: {str(e)}")

    async def get_user_profile(self, user_id: str):
        """Retrieve a user profile by user ID."""
        return await self.es_client.search_user_profile(user_id)
    
    async def _create_text_from_structured_data(self, structured_data: dict) -> str:
        """Convert structured profile data to text format for embedding."""
        sections = []
        
        if summary := structured_data.get("summary"):
            sections.append(f"Summary:\n{summary}")

        if experience := structured_data.get("experience"):
            exp_entries = []
            for exp in experience:
                entry = f"Role: {exp.get('title', '')}\n"
                entry += f"Company: {exp.get('company', '')}\n"
                entry += f"Period: {exp.get('startDate', '')} - {exp.get('endDate', '')}\n"
                entry += f"Description: {exp.get('description', '')}"
                exp_entries.append(entry)
            
            if exp_entries:
                sections.append("Experience:\n" + "\n\n".join(exp_entries))

        if skills := structured_data.get("skills"):
            sections.append("Skills:\n" + ", ".join(skills))

        if education := structured_data.get("education"):
            edu_entries = []
            for edu in education:
                entry = f"Degree: {edu.get('degree', '')} in {edu.get('field', '')}\n"
                entry += f"Institution: {edu.get('institution', '')}\n"
                entry += f"Period: {edu.get('startDate', '')} - {edu.get('endDate', '')}"
                edu_entries.append(entry)
            
            if edu_entries:
                sections.append("Education:\n" + "\n\n".join(edu_entries))

        return "\n\n".join(sections)
