from typing import Dict, Optional
import httpx
from fastapi import HTTPException
from app.core.config import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

class AuthService:
    def get_google_auth_url(self) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send",
            "access_type": "offline",
            "prompt": "consent"
        }
        # Manual construction to ensure correct encoding
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{GOOGLE_AUTH_URL}?{query_string}"

    async def verify_google_token(self, code: str) -> Dict:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            
            response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to retrieve token from Google")
            
            tokens = response.json()
            access_token = tokens.get("access_token")
            
            # Get user info
            user_response = await client.get(
                GOOGLE_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                 raise HTTPException(status_code=400, detail="Failed to retrieve user info from Google")
            
            return {
                "user_info": user_response.json(),
                "tokens": tokens
            }

auth_service = AuthService()
