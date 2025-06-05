from openai import AsyncOpenAI

class OpenAIEmbeddingClient:
    """Client for generating text embeddings using the OpenAI API."""
    def __init__(self):
        self.client = AsyncOpenAI()

    async def create(self, input):
        """Returns a response that contains embedding for the given input text."""
        return await self.client.embeddings.create(model="text-embedding-3-small", input=input)