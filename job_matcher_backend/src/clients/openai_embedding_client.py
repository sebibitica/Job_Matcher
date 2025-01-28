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
    print(client.create(f'''"job_title: Senior Full Stack Developer Python/React,
"company": "QuantumTech Solutions",
  "location": "Remote (Global)",
  "description": """
    We're seeking an experienced Full Stack Developer to lead development of our AI-powered analytics platform. 

    **Key Responsibilities:**
    - Design and implement scalable microservices using Python 3.11+ and FastAPI
    - Develop responsive front-end interfaces with React 18+ and TypeScript
    - Optimize PostgreSQL queries and database architecture
    - Containerize applications using Docker and orchestrate with Kubernetes
    - Implement CI/CD pipelines with GitHub Actions
    - Collaborate on machine learning integration with PyTorch models
    - Conduct code reviews and mentor junior developers

    **Requirements:**
    - 5+ years production experience with Python and React
    - Expertise in RESTful API design and GraphQL implementation
    - Strong understanding of JWT authentication and OAuth2 flows
    - Experience with cloud platforms (AWS/GCP/Azure)
    - Familiarity with WebSockets and real-time data streaming
    - Proficiency in testing frameworks (pytest, Jest, Cypress)

    **Nice to Have:**
    - Experience with TensorFlow Serving or Triton Inference Server
    - Knowledge of WebAssembly (WASM) integration
    - Contributions to open source projects
    - Understanding of LLM integration patterns

    **What We Offer:**
    - Competitive salary ($160k-$200k) + equity
    - Fully remote work with flexible hours
    - Annual tech budget ($3000) for gear/software
    - Conference and training stipend
    - Premium health insurance including dental/vision
  """'''))