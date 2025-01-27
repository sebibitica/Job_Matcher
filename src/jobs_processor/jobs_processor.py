import json
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient

def process_jobs():
    # Initialize clients
    embedding_client = OpenAIEmbeddingClient()
    es_client = ElasticsearchClient()

    with open('sample_data/jobs.json', 'r') as file:
        jobs_data = json.load(file)

    for index, job in enumerate(jobs_data, start=1):
        try:
            # Generate embedding text
            embedding_text = f"{job['job_title']}\n{job['description']}"
            
            # Get embedding
            embedding_response = embedding_client.create(embedding_text)
            embedding = embedding_response.data[0].embedding
            
            # Add embedding to job data
            job['embedding'] = embedding
            
            # Index in Elasticsearch
            response = es_client.index_job(f"job_{index}", job)
            
            print(f"Indexed job {index}: {response['result']}")

        except Exception as e:
            print(f"Error processing job {index}: {str(e)}")

if __name__ == "__main__":
    process_jobs()