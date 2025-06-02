import numpy as np
from src.clients.openai_embedding_client import OpenAIEmbeddingClient
from src.clients.openai_gpt_client import OpenAIGPTClient
from src.cv_processor.cv_processor import CVProcessor
import asyncio

# TEST FOR DIFFERENCE BETWEEN NORMAL EMBEDDING VS GPT-PREPROCESSED EMBEDDING

# Results: GPT preprocessing significantly improves similarity score

async def standardize_cv(gpt_client: OpenAIGPTClient, cv_raw: str) -> str:
    """Standardize CV text using GPT"""
    prompt = f"""
Te rog să extragi și să structurezi informațiile din acest CV, ideal pentru a fi comparat semantic cu o descriere de job, punând accent pe domeniul de activitate. Pentru fiecare secțiune, menționează cum se leagă de domeniul principal de activitate al persoanei.
Folosește un format simplu, fără caractere speciale sau markdown.

Extrage și formatează informația în următoarele secțiuni:
Domeniu de activitate principal:
Subdomenii sau industrii conexe:

Experiență în domeniu:
- Nume roluri ocupate (specifică domeniul pentru fiecare):
- Ani de experiență în domeniu:
- Tehnologii / unelte specifice domeniului:
- Responsabilități specifice domeniului:
- Metodologie de lucru în domeniu:
- Tip de muncă:

CV brut:
"""
    messages = [{"role":"system", "content":prompt},{"role": "user", "content": cv_raw}]
    response = await gpt_client.create(messages, temperature=0.7)
    return response.choices[0].message.content

async def standardize_job(gpt_client: OpenAIGPTClient, job_raw: str) -> str:
    """Standardize job description using GPT"""
    prompt = f"""
Te rog să extragi și să structurezi informațiile din această descriere de job, ideal pentru a fi comparat semantic cu un CV profesional, punând accent pe domeniul de activitate.
Folosește un format simplu, fără caractere speciale sau markdown.

Structurează astfel:
Domeniul principal:
Subdomenii implicate:

Cerințe specifice domeniului:
- Titlul rolului în domeniu:
- Ani de experiență necesari în domeniu:
- Tehnologii / unelte specifice domeniului:
- Responsabilități specifice domeniului:
- Cerințe obligatorii pentru domeniu:
- Tip de muncă în domeniu:
- Alte detalii relevante:

Descriere job:
"""
    messages = [{"role":"system", "content":prompt},{"role": "user", "content": job_raw}]
    response = await gpt_client.create(messages, temperature=0.7)
    return response.choices[0].message.content

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))



construction_job = """
Construction Worker / General Laborer

We are currently seeking experienced construction workers to join our growing team.
Required experience: 3+ years in construction
Main duties: Building foundations, operating power tools, following construction plans
Must be able to: lift heavy materials, work outdoors in all weather conditions
Equipment used: Power tools, hand tools, construction machinery
Safety certifications required
Schedule: Monday-Friday, 7AM-4PM
Location: On-site work in Bucharest
Salary: 4000-5000 RON/month
Benefits: Health insurance, overtime pay, safety equipment provided
"""

electrician_job = """
Residential & Commercial Electrician

Seeking licensed electrician with minimum 5 years experience.
Main responsibilities:
- Installing and maintaining electrical systems
- Reading and following electrical plans and blueprints
- Troubleshooting electrical issues
- Wiring new constructions and renovations
Required qualifications:
- Valid electrician license
- Experience with both residential and commercial projects
- Knowledge of electrical codes and safety regulations
Tools & equipment: Complete set of electrical tools, testing equipment
Work type: Full-time, on-call rotation for emergencies
Location: Various sites in Bucharest area
Schedule: 40 hours/week + emergency calls
Benefits: Company van, tool allowance, performance bonuses
"""

programmer_job = """
Software Engineer / Full Stack Developer
We are looking for a skilled software engineer with expertise in full stack development.
Required experience: 4+ years in software
development
Main responsibilities:
- Designing and implementing web applications
- Collaborating with cross-functional teams
- Writing clean, maintainable code
- Debugging and optimizing existing applications
Must have experience with:
- JavaScript frameworks (React, Angular)
- Backend technologies (Node.js, Python)
- Database management (SQL, NoSQL)
- Version control systems (Git)
- Agile development methodologies
- Excellent problem-solving skills
- Strong communication skills
- Ability to work independently and in a team
"""

async def main():
    embedding_client = OpenAIEmbeddingClient()
    gpt_client = OpenAIGPTClient()
    
    cv_text = CVProcessor.extract_text(open("sample_data/BiticaSebastianCV.pdf", "rb"))
    
    # Example job description
    job_text = programmer_job

    # Test 1: Direct embedding without GPT processing
    print("\nTesting direct embedding similarity:")
    resp_cv_emb = await embedding_client.create(cv_text)
    cv_emb = resp_cv_emb.data[0].embedding

    resp_job_emb = await embedding_client.create(job_text)
    job_emb = resp_job_emb.data[0].embedding
    raw_similarity = cosine_similarity(cv_emb, job_emb)
    print(f"Raw similarity score: {raw_similarity:.3f}")

    # Test 2: GPT processing before embedding
    print("\nTesting similarity with GPT preprocessing:")
    cv_processed = await standardize_cv(gpt_client, cv_text)
    job_processed = await standardize_job(gpt_client, job_text)
    
    resp_cv_processed_emb = await embedding_client.create(cv_processed)
    cv_processed_emb = resp_cv_processed_emb.data[0].embedding
    resp_job_processed_emb = await embedding_client.create(job_processed)
    job_processed_emb = resp_job_processed_emb.data[0].embedding
    processed_similarity = cosine_similarity(cv_processed_emb, job_processed_emb)
    print(f"Processed similarity score: {processed_similarity:.3f}")

    # Print processed texts for comparison
    print("\nProcessed CV:")
    print(cv_processed)
    print("\nProcessed Job Description:")
    print(job_processed)

if __name__ == "__main__":
    asyncio.run(main())