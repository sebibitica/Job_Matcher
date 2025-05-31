from ..clients.openai_gpt_client import OpenAIGPTClient

class TextPreprocessor:
    def __init__(self):
        self.gpt_client = OpenAIGPTClient()

    def preprocess_cv(self, cv_raw: str) -> str:
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
        response = self.gpt_client.create(messages, temperature=0.7)
        return response.choices[0].message.content
    
    def preprocess_job(self, job_raw: str) -> str:
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
        response = self.gpt_client.create(messages, temperature=0.7)
        return response.choices[0].message.content