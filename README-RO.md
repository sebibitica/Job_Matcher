# Platformă Job Matcher

## Demo Live

**Încercați aplicația la [https://jobsmatcher.xyz](https://jobsmatcher.xyz)**

Versiunea live este complet hostată cu o bază de date populată ce conține numeroase anunțuri de joburi gata pentru a fi încercate. Pentru rularea si testarea aplicației locală, [urmați instrucțiunile de configurare de mai jos](#configurare).

## Prezentare generală

**Job Matcher** este o platformă bazată pe inteligență artificială care potrivește CV-urile utilizatorilor cu oportunități relevante de angajare și îi ajută să se pregătească pentru interviuri cu un Simulator de Interviu AI. Platforma oferă:

- **Potrivire personalizată de joburi:** Încărcați CV-ul sau completați profilul pentru a primi recomandări personalizate de locuri de muncă.
- **Simulare de interviu AI:** Exersați interviuri pentru joburi specifice cu feedback și coaching instantaneu de la AI.
- **Urmărirea aplicațiilor:** Salvați și gestionați joburile la care ați aplicat.

Platforma constă dintr-un **frontend React + TypeScript** și un **backend Python FastAPI**. Utilizează Firebase pentru autentificare, Firestore pentru gestionarea datelor de interviuri, OpenAI pentru funcționalități bazate pe AI, și Elasticsearch & Kibana pentru gestionarea datelor despre joburi și utilizatori.

---

## Caracteristici

- **Încărcare și analiză CV:** Încărcați CV-uri în format PDF/DOCX pentru potrivirea instantanee cu joburi.
- **Introducere manuală a profilului:** Introduceți manual experiența, educația și abilitățile.
- **Preprocesare și îmbunătățire CV/Profil:** Îmbunătățirea și standardizarea automată a CV-ului sau profilului folosind AI bazat pe GPT.
- **Potrivire de joburi prin similaritate KNN:** Potrivire avansată de joburi folosind căutarea de similaritate semantică k-nearest neighbors (KNN).
- **Coach de interviu AI:** Exersați interviuri cu AI, primiți feedback și îmbunătățiți-vă.
- **Urmăritor de aplicații pentru joburi:** Marcați joburile ca aplicate și vizualizați istoricul aplicațiilor.
- **Autentificare securizată:** Înregistrare, autentificare și OAuth Google prin Firebase.
- **Interfață responsivă:** Interfață modernă, optimizată pentru dispozitive mobile.

---

## Configurare

### Cerințe preliminare

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

### Variabile de mediu

Copiați `.env.example` în [`.env`](.env ) și completați cu datele dvs. de autentificare:

```sh
cp .env.example .env
```

**Chei API și credențiale necesare:**

- **OpenAI API Key**: Obțineți de la [OpenAI Platform](https://platform.openai.com/account/api-keys)
- **Google Maps API Key**: Obțineți de la [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/credentials)
- **Adobe PDF Services**: Obțineți de la [Adobe Developer Console](https://developer.adobe.com/document-services/apis/pdf-services/)
- **Proiect Firebase**: Creați un proiect la [Firebase Console](https://console.firebase.google.com/)

**Configurare importantă Firebase:**

1. **Backend:**  
   Descărcați credențialele contului de serviciu Firebase ca `firebaseCredentials.json` și plasați-le în directorul `job_matcher_backend/`.

2. **Frontend:**  
   Actualizați configurația Firebase în `job_matcher_frontend/src/firebase/firebase.ts` cu valorile proprii `firebaseConfig` din setările proiectului Firebase.

---

## Rularea aplicației

Întreaga platformă poate fi lansată folosind Docker Compose:

```sh
# Pornirea tuturor serviciilor
docker-compose up --build
```

Aceasta va porni:
- Baza de date Elasticsearch
- Kibana (opțional, pentru vizualizarea bazei de date)
- API Backend
- Aplicația web Frontend

**Accesarea aplicației:**
- **Frontend:** http://localhost:3000
- **API Backend:** http://localhost:8000/docs
- **Kibana (opțional):** http://localhost:5601

Pentru a opri aplicația:

```sh
docker-compose down
```

### Important: Popularea inițială a bazei de date

**Notă:** Când rulați aplicația local pentru prima dată, baza de date Elasticsearch va fi goală. Va trebui să rulați procesorul de joburi pentru a o popula cu anunțuri de locuri de muncă înainte de a putea vedea rezultate de potrivire.

## Procesarea joburilor

Sistemul rulează automat procesorul de joburi zilnic la ora 14:00 UTC pentru a prelua și indexa noi anunțuri de locuri de muncă, dar trebuie să-l rulați manual pentru popularea inițială a bazei de date.

### Rularea manuală a procesorului de joburi

Pentru a popula baza de date cu anunțuri de joburi:

```sh
# Accesați containerul backend
docker exec -it backend /bin/bash

# Rulați procesorul de joburi
python3 -m src.jobs_processor.jobs_processor_parallel
```

Acest proces poate dura ceva timp, în funcție de resursele sistemului. Odată finalizat, baza de date va fi populată cu anunțuri de joburi și aplicația va fi gata de utilizare.

Puteți verifica dacă datele au fost încărcate prin:
1. Verificarea Kibana la http://localhost:5601 dacă este activat
2. Vizitarea aplicației frontend și căutarea de joburi
3. Verificarea jurnalelor de procesare a joburilor cu `docker exec -it backend tail -f /var/log/jobs_processor.log`

---

## Structura directorului

```
job_matcher/
├── docker-compose.yml  # Fișier principal Docker Compose
├── .env                # Variabile de mediu
├── job_matcher_backend/
│   ├── api.py          # Aplicație principală FastAPI
│   ├── src/            # Cod sursă backend
│   └── ...
├── job_matcher_frontend/
│   ├── src/            # Componente React frontend
│   └── ...
└── README.md
```

---

## Erori la pornire

- **Serviciile nu pornesc:** Verificați jurnalele Docker cu `docker-compose logs`
- **Erori de conexiune API:** Asigurați-vă că variabilele de mediu sunt setate corect
- **Nu se afișează joburi:** Procesarea inițială a joburilor poate dura ceva timp pentru a se finaliza

---

## Tehnologii folosite

- **Frontend:** React, TypeScript, Vite
- **Backend:** FastAPI, Python
- **Baza de date:** Elasticsearch + Firestore
- **Autentificare:** Firebase
- **AI:** OpenAI API
- **Containerizare:** Docker

---