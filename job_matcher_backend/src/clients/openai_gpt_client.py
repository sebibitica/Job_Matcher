from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIGPTClient:
    """Client for generating chat completions using the OpenAI GPT API."""
    def __init__(self):
        self.client = OpenAI()

    def create(self, messages, model="gpt-4o-mini", temperature=0.7):
        """ Returns a chat completion response for the given messages."""
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

if __name__ == "__main__":
    client = OpenAIGPTClient()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, can you help me?"}
    ]
    response = client.create(messages)
    print(response.choices[0].message['content'])