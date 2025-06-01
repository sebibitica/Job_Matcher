import numpy as np
from src.clients.openai_embedding_client import OpenAIEmbeddingClient
from src.clients.openai_gpt_client import OpenAIGPTClient
from src.cv_processor.cv_processor import CVProcessor
import asyncio

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
Ideal Candidate:
​5+ years of experience in software development.
More than 3 years of front-end development experience with React using TypeScript or JavaScript.
Minimum of 2 years experience with 2 or more server-side programming languages, preferably Java and/or TypeScript.
Extensive experience in building and maintaining scalable, responsive user interfaces using modern languages and frameworks.
Proficient in using and consuming GraphQL and REST APIs.
Continuous Quality and Process Improvement.
Advocate of modern engineering best practices, including TDD, cloud computing, DDD, and observability.
Experienced with relational databases such as MySQL and PostgreSQL.
Experience in developing products impacting a large customer base is advantageous.
Preferably holds a university degree in Mathematics or Software Engineering.
Excellent written and verbal communication skills.


Job Description:
The Acceleration team will develop new features and expand the self-serving capabilities of existing systems to handle partner accounts at scale, with initial focus on automating backend operational tasks and improving onboarding and partner setup.

This role provides a hybrid way of working with an onsite presence of 2 days/week.

Key Job Responsibilities and Duties
Building Software Applications: Strong proficiency in front-end programming languages like JavaScript / Typescript and frameworks like React
Writing Quality Code: Ability to write scalable, readable, and reusable code adhering to coding standards, with a focus on refactoring and design patterns to ensure maintainability.
End-to-End Ownership: Independently manage services from development to production, including monitoring application performance and implementing relevant SLIs, SLOs, and KPIs.
Software System Design: Experience in evaluating and selecting architecture solutions that align with business and technology requirements, ensuring adaptability for future enhancements.
Technical Incident Management: Ability to diagnose and resolve live production issues, contributing to reliability through root cause analysis and postmortem documentation.
Continuous Quality Improvement: Identify areas for process optimization, designing and implementing improvements to enhance performance and efficiency.
Collaborative Communication: Effective in delivering information tailored to audience needs, fostering team collaboration, and actively engaging in discussions to achieve shared goals.
Recruiting: Contributing to the growth of Booking.com through interviewing, on-boarding, or other recruitment efforts

Benefits:
Healthinsurance
Prepaid medical subscription (Regina Maria)
Life insurance
Meal vouchers
Learning wallet
Travel benefit
Annual vacation leave of 25 business days, pro rata with the working period
Birthday day off
Summer break (short Fridays during summer)
Work from Abroad program (up to 20 days/year in EU)
Floating days off
2 Volunteer days/ year
Home office one-time bonus
Bookster
Linkedin learning platform
Headspace
Employee discounts (travel, gym, dental, vision)


Company Description:
Booking Holdings Center of Excellence is part of Booking Holdings, the world's leading provider of online travel and related services, with a rich heritage of digital innovation. The Center provides access to specialized and highly skilled talent, supports projects powered by new and emerging technologies, leverages industry best practices, and fosters collaboration opportunities across all of the Booking Holdings brands, including Booking.com, Priceline, Agoda, KAYAK and OpenTable.

If you are interested to find out more about the Booking Holdings Center of Excellence visit our website: www.bookingholdings-coe.com.

Booking Holdings (NASDAQ: BKNG) is the world’s leading provider of online travel and related services, provided to consumers and local partners in more than 220 countries and territories through five primary consumer facing brands: Booking.com, Priceline, Agoda, KAYAK and OpenTable. The mission of Booking Holdings is to make it easier for everyone to experience the world.
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