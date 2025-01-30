from io import BytesIO
from ..clients.es_client import ElasticsearchClient
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..cv_processor.cv_processor import CVProcessor

class JobsMatcher:
    def __init__(self):
        """ Initialize the JobsMatcher with the CV byte stream """
        self.embedding_client = OpenAIEmbeddingClient()
        self.es_client = ElasticsearchClient()

    def process_cv(self, file_stream: BytesIO):
        """ Process the CV to generate its embedding """
        cv_processor = CVProcessor(file_stream, self.embedding_client)
        return cv_processor.process()

    def find_matching_jobs(self, cv_embedding, top_k: int = 10, exclude_job_ids: list = None) -> dict:
        """ Find top K matching jobs based on the CV embedding """
        print("\nSearching for matching jobs...")
        if not cv_embedding:
            raise ValueError("CV embedding not received for matching.")
        
        return self.es_client.search_jobs_by_embedding(cv_embedding, k=top_k, exclude_job_ids=exclude_job_ids)

    def get_matching_jobs_by_file(self, file_stream: BytesIO, top_k: int = 10):
        """ Process the CV and find top K matching jobs """
        cv_embedding = self.process_cv(file_stream)
        return self.find_matching_jobs(cv_embedding, top_k)

    def get_matching_jobs_with_resume_id(self, resume_id: str, user_id: str, top_k: int = 10) -> dict:
        """ Get matching jobs using a resume ID to fetch its embedding """
        print("\nSearching for matching jobs based on resume ID...")
        cv_embedding = self.es_client.get_resume_embedding(resume_id, user_id)
        
        # Fetch applied job IDs for the user
        applied_jobs_response = self.es_client.get_user_applications(user_id)
        applied_job_ids = [hit["_source"]["job_id"] for hit in applied_jobs_response["hits"]["hits"]]
        
        # Pass applied_job_ids to exclude them from the search results
        return self.find_matching_jobs(cv_embedding, top_k, exclude_job_ids=applied_job_ids)

    @staticmethod
    def print_results(results: dict):
        """Print formatted results"""
        print("\nTop Matching Jobs:")
        for idx, hit in enumerate(results['hits']['hits'], 1):
            score = hit['_score']
            job = hit['_source']
            print(f"\n{idx}. {job['job_title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Job URL: {job['job_url']}")
            print(f"   Match Score: {score:.3f}")


if __name__ == "__main__":
    matcher = JobsMatcher()
    try:
        # results = matcher.get_matching_jobs_by_file(open("sample_data/example4.docx", "rb"))
        results=matcher.get_matching_jobs_with_resume_id(user_id="A81eScgtsdbAKIhVzUtXclWk7A02", resume_id="1a116567-fa47-478b-aa57-500b7a1588fe")
        matcher.print_results(results)
    except Exception as e:
        print(f"Error: {str(e)}")