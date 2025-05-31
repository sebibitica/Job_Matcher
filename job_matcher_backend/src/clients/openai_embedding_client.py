from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIEmbeddingClient:
    """Client for generating text embeddings using the OpenAI API."""
    def __init__(self):
        self.client = OpenAI()

    def create(self, input):
        """Returns a response that contains embedding for the given input text."""
        return self.client.embeddings.create(model="text-embedding-3-small", input=input)
    
if __name__ == "__main__":
    embedding_client = OpenAIEmbeddingClient()
    sample_text = "This is a sample text for generating embeddings."
    response = embedding_client.create(sample_text)
    print(response.data[0].embedding)