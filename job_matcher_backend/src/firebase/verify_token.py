from fastapi import Request, HTTPException
from firebase_admin import auth, credentials
import firebase_admin

# Initialize Firebase
cred = credentials.Certificate("./firebaseCredentials.json")
firebase_admin.initialize_app(cred)

async def get_current_user(request: Request):
    """Middleware to validate Firebase token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    try:
        token = auth_header.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication credentials"
        )