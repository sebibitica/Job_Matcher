from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIGPTClient:
    def __init__(self):
        self.client = OpenAI()

    def create(self, messages, model="gpt-4o-mini", temperature=0.7):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )