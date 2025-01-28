from io import BytesIO
from ..clients.es_client import ElasticsearchClient
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..cv_processor.cv_processor import CVProcessor

class JobsMatcher:
    def __init__(self, file_stream: BytesIO):
        """ Initialize the JobsMatcher with the CV byte stream """
        self.file_stream = file_stream
        self.embedding_client = OpenAIEmbeddingClient()
        self.es_client = ElasticsearchClient()
        self.cv_embedding = None

    def process_cv(self):
        """ Process the CV to generate its embedding """
        cv_processor = CVProcessor(self.file_stream, self.embedding_client)
        response = cv_processor.process()
        self.cv_embedding = response

    def find_matching_jobs(self, top_k: int = 10) -> dict:
        """ Find top K matching jobs based on the CV embedding """
        print("\nSearching for matching jobs...")
        if not self.cv_embedding:
            raise ValueError("CV embedding not generated. Call process_cv() first.")
        
        return self.es_client.search_jobs_by_embedding(self.cv_embedding, k=top_k)

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
    matcher = JobsMatcher(open("sample_data/example4.docx","rb"))
    try:
        matcher.process_cv()
        results = matcher.find_matching_jobs()
        matcher.print_results(results)
    except Exception as e:
        print(f"Error: {str(e)}")