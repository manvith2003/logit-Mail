from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid

class EmailSendRequest(BaseModel):
    to: List[EmailStr]
    cc: Optional[List[EmailStr]] = []
    bcc: Optional[List[EmailStr]] = []
    subject: str
    body: str

class EmailResponse(BaseModel):
    id: uuid.UUID
    message_id: str
    thread_id: str
    label_ids: Optional[str] # Keep as string for now to avoid crash
    
    subject: Optional[str]
    sender: Optional[str]
    recipient: Optional[str]
    snippet: Optional[str]
    body_text: Optional[str]
    received_at: Optional[datetime]
    is_processed: bool
    
    event_title: Optional[str]
    event_date: Optional[datetime]
    deadline: Optional[datetime]
    action_required: bool

    class Config:
        from_attributes = True
