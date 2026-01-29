from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.services.auth_service import auth_service
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/login/google")
async def login_google():
    """
    Redirects the user to the Google OAuth login page.
    """
    print("DEBUG: /login/google endpoint was hit!")
    auth_url = auth_service.get_google_auth_url()
    print(f"DEBUG: Redirecting to {auth_url}")
    return RedirectResponse(url=auth_url)

@router.get("/callback/google")
async def callback_google(code: str, db: AsyncSession = Depends(get_db)):
    """
    Handles the callback from Google OAuth.
    Exchanges the authorization code for an access token and retrieves user info.
    Creates or updates the user in the database.
    """
    try:
        auth_data = await auth_service.verify_google_token(code)
        user_info = auth_data["user_info"]
        tokens = auth_data["tokens"]
        
        email = user_info.get("email")
        if not email:
             raise HTTPException(status_code=400, detail="Google did not return an email address")

        # Check if user exists
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()

        expiry_in = tokens.get("expires_in", 3600)
        token_expiry = datetime.utcnow() + timedelta(seconds=expiry_in)

        if not user:
            # Create new user
            user = User(
                email=email,
                full_name=user_info.get("name"),
                picture=user_info.get("picture"),
                google_access_token=tokens.get("access_token"),
                google_refresh_token=tokens.get("refresh_token"),
                token_expiry=token_expiry,
                is_active=True
            )
            db.add(user)
        else:
            # Update existing user tokens
            user.google_access_token = tokens.get("access_token")
            # Only update refresh token if provided (it's not always provided by Google on re-auth)
            if tokens.get("refresh_token"):
                user.google_refresh_token = tokens.get("refresh_token")
            user.token_expiry = token_expiry
            user.picture = user_info.get("picture")
            user.full_name = user_info.get("name")
        
        await db.commit()
        await db.refresh(user)

        # Redirect to frontend dashboard with user info (in production use secure cookies/tokens)
        frontend_url = "http://localhost:5173/dashboard"
        return RedirectResponse(
            url=f"{frontend_url}?user_id={user.id}&login_success=true"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
