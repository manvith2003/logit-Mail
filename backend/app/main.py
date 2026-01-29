from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For debugging, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import users, auth, emails

# ... existing middleware code ...

app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(emails.router, prefix=f"{settings.API_V1_STR}/emails", tags=["emails"])
from app.api import calendar
app.include_router(calendar.router, prefix=f"{settings.API_V1_STR}/calendar", tags=["calendar"])
# AI features removed

@app.get("/")
def root():
    return {"message": "Welcome to Logit Mail API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
