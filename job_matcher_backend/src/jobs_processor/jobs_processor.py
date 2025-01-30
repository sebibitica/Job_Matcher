import json
from ..clients.openai_embedding_client import OpenAIEmbeddingClient
from ..clients.es_client import ElasticsearchClient
import hashlib

def generate_job_id(job: dict) -> str:
    unique_job_data = f"{job['company']}|{job['title']}|{job['job_url']}"
    return hashlib.sha256(unique_job_data.encode()).hexdigest()

def process_jobs():
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

            job['embedding'] = embedding
            
            job_id = generate_job_id(job)

            response = es_client.index_job(job_id, job)
            
            print(f"Indexed job {index}: {response['result']}")

        except Exception as e:
            print(f"Error processing job {index}: {str(e)}")

if __name__ == "__main__":
    process_jobs()