import json
from google.cloud.firestore_v1.async_client import AsyncClient
from google.oauth2 import service_account

class FirestoreClient:
    """Async Firestore client wrapper using service account credentials."""
    def __init__(self, credentials_path: str = "./firebaseCredentials.json"):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        
        with open(credentials_path) as f:
            self.project_id = json.load(f)["project_id"]

        self.client = AsyncClient(
            project=self.project_id,
            credentials=self.credentials
        )