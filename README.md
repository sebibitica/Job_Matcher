# Job Matcher Platform

## Overview

**Job Matcher** is an AI-powered platform that matches user CVs with relevant job opportunities and helps them prepare for interviews with an AI Interview Simulator. The platform provides:

- **Personalized Job Matching:** Upload your resume or complete your profile to receive tailored job recommendations.
- **AI Interview Simulation:** Practice interviews for specific jobs with instant AI feedback and coaching.
- **Application Tracking:** Save and manage jobs you've applied to.

The platform consists of a **React + TypeScript frontend** and a **FastAPI Python backend**. It uses Firebase for authentication, Firestore for interviews data management, OpenAI for AI-powered features, and Elasticsearch & Kibana for job and users data management.

---

## Features

- **Resume Upload & Parsing:** Upload PDF/DOCX resumes for instant job matching.
- **Manual Profile Entry:** Enter experience, education, and skills manually.
- **Resume/Profile Preprocessing & Enhancement:** Automatically improve and standardize your resume or profile using GPT-powered AI.
- **KNN Similarity Job Matching:** Advanced job matching using k-nearest neighbors (KNN) semantic similarity search.
- **AI Interview Coach:** Practice interviews with AI, get feedback, and improve.
- **Job Application Tracker:** Mark jobs as applied and view your application history.
- **Secure Authentication:** Sign up, login, and Google OAuth via Firebase.
- **Responsive UI:** Modern, mobile-friendly interface.

---

## Setup & Configuration

### Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

### Environment Variables

Copy `.env.example` to [`.env`](.env ) and fill in your credentials:

```sh
cp .env.example .env
```

**Required API Keys & Credentials:**

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/account/api-keys)
- **Google Maps API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/credentials)
- **Adobe PDF Services**: Get from [Adobe Developer Console](https://developer.adobe.com/document-services/apis/pdf-services/)
- **Firebase Project**: Create a project at [Firebase Console](https://console.firebase.google.com/)

**Important Firebase Setup:**

1. **Backend:**  
   Download your Firebase service account credentials as `firebaseCredentials.json` and place it in the `job_matcher_backend/` directory.

2. **Frontend:**  
   Update the Firebase configuration in `job_matcher_frontend/src/firebase/firebase.ts` with your own `firebaseConfig` values from your Firebase project settings.

---

## Running the Application

The entire platform can be launched using Docker Compose:

```sh
# Start all services
docker-compose up -d
```

This will start:
- Elasticsearch database
- Kibana (optional, for database visualization)
- Backend API
- Frontend web application

**Access the Application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs
- **Kibana (optional):** http://localhost:5601

To stop the application:

```sh
docker-compose down
```

---

## Automated Jobs Processing

The system automatically runs the jobs processor daily at 2PM UTC to fetch and index new job listings.

### Manual Jobs Processing

If you want to run the jobs processor manually:

```sh
# Access the backend container
docker exec -it backend /bin/bash

# Run the jobs processor
python3 -m src.jobs_processor.jobs_processor_parallel
```

---

## Directory Structure

```
job_matcher/
├── docker-compose.yml  # Main Docker Compose file
├── .env                # Environment variables
├── job_matcher_backend/
│   ├── api.py          # Main FastAPI application
│   ├── src/            # Backend source code
│   └── ...
├── job_matcher_frontend/
│   ├── src/            # Frontend React components
│   └── ...
└── README.md
```

---

## Troubleshooting

- **Services not starting:** Check Docker logs with `docker-compose logs`
- **API connection errors:** Ensure environment variables are set correctly
- **No jobs showing:** The initial job processing may take time to complete

---

## Tech Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** FastAPI, Python
- **Database:** Elasticsearch + Firestore
- **Authentication:** Firebase
- **AI:** OpenAI API
- **Containerization:** Docker



---

**Enjoy using Job Matcher!**