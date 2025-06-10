from src.clients.es_client import ElasticsearchClient
from src.clients.firestore.interviews_firestore import InterviewsManager
from openai import AsyncOpenAI
from src.user_profile.profile_manager import ProfileManager
from src.clients.openai_embedding_client import OpenAIEmbeddingClient
from src.clients.openai_gpt_client import OpenAIGPTClient
from src.preprocessor.preprocessor import TextPreprocessor
from src.jobs_matcher.jobs_matcher import JobsMatcher
from src.applied_jobs.applied_jobs_manager import AppliedJobsManager
from src.user_profile.profile_structurer.profile_structurer import ProfileStructurer

es_client = ElasticsearchClient()
embedding_client = OpenAIEmbeddingClient()
openai_clean_client = AsyncOpenAI()
gpt_client = OpenAIGPTClient()

preprocessor = TextPreprocessor()
profile_structurer = ProfileStructurer()

interviews_manager = InterviewsManager()
profile_manager = ProfileManager(embedding_client, es_client, preprocessor, profile_structurer)
jobs_matcher = JobsMatcher(embedding_client, es_client, preprocessor)
applied_jobs_manager = AppliedJobsManager(es_client)

def get_es_client():
    return es_client

def get_interviews_manager():
    return interviews_manager

def get_openai_clean_client():
    return openai_clean_client

def get_profile_manager():
    return profile_manager

def get_applied_jobs_manager():
    return applied_jobs_manager

def get_jobs_matcher():
    return jobs_matcher