from ...clients.openai_gpt_client import OpenAIGPTClient

class ProfileStructurer:
    def __init__(self):
        self.gpt_client = OpenAIGPTClient()

    async def structure_profile(self, cv_raw: str) -> str:
        """Structure CV text into a json using GPT"""
        prompt = """
        Primești mai jos un CV sub formă de text. Te rog să extragi informațiile relevante și să le structurezi într-un JSON cu următorul format:

        {
        \"summary\": \"Scurt rezumat profesional (maxim 2-3 fraze)\",
        \"experience\": [
            {
            \"title\": \"Titlul jobului\",
            \"company\": \"Numele companiei\",
            \"startDate\": \"YYYY-MM\",
            \"endDate\": \"YYYY-MM sau 'Present' dacă este actual\",
            \"description\": \"Descriere scurtă a responsabilităților și realizărilor\"
            }
            // Poți adăuga mai multe obiecte pentru fiecare experiență profesională
        ],
        \"education\": [
            {
            \"degree\": \"Tipul diplomei (ex: Bachelor, Master, etc.)\",
            \"field\": \"Domeniul de studiu\",
            \"institution\": \"Numele instituției\",
            \"startDate\": \"YYYY-MM\",
            \"endDate\": \"YYYY-MM\"
            }
            // Poți adăuga mai multe obiecte pentru fiecare diplomă/școală
        ],
        \"skills\": [\"listă de skill-uri relevante, sub formă de stringuri\"]
        }

        Te rog să respecți exact această structură și să nu adaugi alte câmpuri. Completează câmpurile cu informațiile găsite în CV. Dacă anumite informații lipsesc, lasă câmpul respectiv gol sau ca listă goală.

        Păstrează textul exact în limba originală în care apare în CV. Nu traduce niciun text în română sau altă limbă.
        CV:
        """
        messages = [{"role":"system", "content":prompt},{"role": "user", "content": cv_raw}]
        response = await self.gpt_client.create(messages, temperature=0.7)
        return response.choices[0].message.content