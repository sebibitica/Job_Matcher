from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials
import firebase_admin
import asyncio

cred = credentials.Certificate("./firebaseCredentials.json")
firebase_admin.initialize_app(cred)

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    """Dependency to validate Firebase token and extract user ID."""
    if not credentials:
        raise HTTPException(
            status_code=401, 
            detail="Missing authentication credentials"
        )
    try:
        token = credentials.credentials
        decoded_token = await asyncio.to_thread(auth.verify_id_token, token, clock_skew_seconds=10)
        return decoded_token['uid']
    except Exception as e:
        print("Error verifying ID token: ", e)
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication credentials"
        )