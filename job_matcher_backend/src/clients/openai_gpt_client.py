from openai import AsyncOpenAI

class OpenAIGPTClient:
    """Client for generating chat completions using the OpenAI GPT API."""
    def __init__(self):
        self.client = AsyncOpenAI()

    async def create(self, messages, model="gpt-4o-mini", temperature=0.7):
        """ Returns a chat completion response for the given messages."""
        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )