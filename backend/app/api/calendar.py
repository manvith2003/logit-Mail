from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.models.user import User
from sqlalchemy import select
from app.services.calendar_service import calendar_service

router = APIRouter()

class CalendarEventRequest(BaseModel):
    user_id: str
    title: str
    start_time: str # ISO format
    description: str = None

@router.post("/events")
async def create_calendar_event(request: CalendarEventRequest, db: AsyncSession = Depends(get_db)):
    """
    Creates an event in the user's primary Google Calendar.
    """
    try:
        # Get user
        result = await db.execute(select(User).filter(User.id == request.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        event = calendar_service.create_event(
            user=user,
            title=request.title,
            start_time=request.start_time,
            description=request.description
        )
        
        return {"status": "success", "event_link": event.get('htmlLink')}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
