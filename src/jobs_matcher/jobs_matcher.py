import sys
from pathlib import Path
from ..clients.es_client import ElasticsearchClient
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..cv_processor.cv_processor import CVProcessor

def main(cv_path):
    # Initialize clients
    embedding_client = OpenAIEmbeddingClient()
    es_client = ElasticsearchClient()
    
    # Process CV
    try:
        cv_processor = CVProcessor(cv_path, embedding_client)
        embedding_response = cv_processor.process()
        cv_embedding = embedding_response.data[0].embedding
    except Exception as e:
        print(f"Error processing CV: {str(e)}")
        sys.exit(1)
    
    # Search for matching jobs
    try:
        print("\nSearching for matching jobs...")
        results = es_client.search_jobs_by_embedding(cv_embedding)
        print(results)
        print("\nTop 10 Matching Jobs:")
        for idx, hit in enumerate(results['hits']['hits'], 1):
            score = hit['_score']
            job = hit['_source']
            print(f"\n{idx}. {job['job_title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Match Score: {score:.3f}")
    except Exception as e:
        print(f"Error searching jobs: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    
    main("sample_data/example1.pdf")