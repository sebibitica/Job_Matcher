from io import BytesIO
from ..clients.es_client import ElasticsearchClient
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..cv_processor.cv_processor import CVProcessor
from ..preprocessor.preprocessor import TextPreprocessor
from ..types.types import MatchedJob

class JobsMatcher:
    def __init__(self):
        """ Initialize the JobsMatcher with the CV byte stream """
        self.embedding_client = OpenAIEmbeddingClient()
        self.es_client = ElasticsearchClient()
        self.preprocessor = TextPreprocessor()

    def process_cv(self, file_stream: BytesIO):
        """ Process the CV to generate its embedding """
        return CVProcessor.process_file(file_stream, self.preprocessor, self.embedding_client)

    def find_matching_jobs(self, cv_embedding, top_k: int = 15, exclude_job_ids: list = None) -> list[MatchedJob]:
        """ Find top K matching jobs based on the CV embedding """
        if not cv_embedding:
            raise ValueError("CV embedding not received for matching.")
        
        return self.es_client.search_jobs_by_embedding(cv_embedding, k=top_k, exclude_job_ids=exclude_job_ids)

    def get_matching_jobs_by_file(self, file_stream: BytesIO, top_k: int = 15)-> list[MatchedJob]:
        """ Process the CV and find top K matching jobs """
        cv_embedding = self.process_cv(file_stream)
        return self.find_matching_jobs(cv_embedding, top_k)
    
    def get_matching_jobs_with_user_id(self, user_id: str, top_k: int = 15) -> list[MatchedJob]:
        """ Get matching jobs using a user ID to fetch its embedding """
        cv_embedding = self.es_client.get_user_embedding(user_id)
        if not cv_embedding:
            raise ValueError("User embedding not found.")
        
        # Fetch applied job IDs for the user
        applied_jobs_response = self.es_client.get_user_applications(user_id)
        applied_job_ids = [hit["_source"]["job_id"] for hit in applied_jobs_response["hits"]["hits"]]
        
        # Pass applied_job_ids to exclude them from the search results
        return self.find_matching_jobs(cv_embedding, top_k, exclude_job_ids=applied_job_ids)

    @staticmethod
    def print_results(results: dict):
        """Print formatted results"""
        if not results:
            print("No matching jobs found.")
            return
        
        print(f"\nFound {len(results)} matching jobs:")
        for job in results:
            print(f"Job ID: {job.id}, Title: {job.job_title}, Company: {job.company}, Score: {job.score:.2f}")


if __name__ == "__main__":
    matcher = JobsMatcher()
    try:
        # Example usage
        with open("sample_data/electrician.docx", "rb") as file:
            cv_stream = BytesIO(file.read())
        
        matching_jobs = matcher.get_matching_jobs_by_file(cv_stream, top_k=10)
        matcher.print_results(matching_jobs)
    except Exception as e:
        print(f"An error occurred: {e}")