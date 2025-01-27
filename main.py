from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="SKILLS: PYTHON, JAVA, C++, C, GO. Years Experience: 2. Remote working."
)

print(response)