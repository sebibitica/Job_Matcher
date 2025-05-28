from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIEmbeddingClient:
    def __init__(self):
        self.client = OpenAI()

    def create(self, input):
        return self.client.embeddings.create(model="text-embedding-3-small", input=input)


if __name__ == "__main__":
    client = OpenAIEmbeddingClient()
    print(client.create(f'Hello, world! This is a test input for the OpenAI embedding client.'))