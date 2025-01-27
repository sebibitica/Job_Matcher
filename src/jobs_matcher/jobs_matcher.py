from pathlib import Path
from ..clients.es_client import ElasticsearchClient
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..cv_processor.cv_processor import CVProcessor

class JobsMatcher:
    def __init__(self, cv_path: str):
        """ Initialize the JobsMatcher with the path to the CV file """
        self.cv_path = Path(cv_path)
        self.embedding_client = OpenAIEmbeddingClient()
        self.es_client = ElasticsearchClient()
        self.cv_embedding = None

    def _validate_file(self):
        """Check if the CV file exists and is valid"""
        if not self.cv_path.exists():
            raise FileNotFoundError(f"CV file not found: {self.cv_path}")
        if self.cv_path.suffix.lower() not in ['.pdf', '.docx']:
            raise ValueError(f"Unsupported file type: {self.cv_path.suffix}")

    def process_cv(self):
        """Process the CV and generate its embedding"""
        self._validate_file()
        
        cv_processor = CVProcessor(str(self.cv_path), self.embedding_client)
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
            print(f"   Match Score: {score:.3f}")

if __name__ == "__main__":
    matcher = JobsMatcher("sample_data/example4.docx")
    try:
        matcher.process_cv()
        results = matcher.find_matching_jobs()
        matcher.print_results(results)
    except Exception as e:
        print(f"Error: {str(e)}")