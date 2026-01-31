from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional
from app.core.database import get_db
from app.services.gmail_service import gmail_service
from app.models.user import User
from app.models.email import Email
from app.schemas.email import EmailSendRequest, EmailResponse

router = APIRouter()

# MVP: Simulating "current user" by passing user_id or assuming single user for now.
# ideally we use a dependency to get the current user from session/token.
async def get_current_user(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

from fastapi import BackgroundTasks

@router.post("/sync")
async def sync_emails(background_tasks: BackgroundTasks, user_id: str, folder: str = "INBOX", limit: int = 50, db: AsyncSession = Depends(get_db)):
    print(f"DEBUG: sync_emails called for user {user_id}, folder={folder}, limit={limit}")
    """
    Triggers email synchronization for the user.
    """
    # Quick hack to get user for MVP testing
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")

    try:
        count, new_email_ids = await gmail_service.fetch_emails(db, user, folder=folder, max_results=limit)
        
        # Trigger AI processing in background
        if new_email_ids:
            print(f"Scheduling background AI processing for {len(new_email_ids)} emails...")
            background_tasks.add_task(gmail_service.process_emails_background, new_email_ids, str(user.id))
            
        return {"message": "Sync complete. AI Agent processing started in background.", "emails_fetched": count}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_email_endpoint(
    request: EmailSendRequest,
    user_id: str = Query(...), # Still using query param for MVP auth
    db: AsyncSession = Depends(get_db)
):
    """
    Sends an email.
    """
    # Get user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        result = await gmail_service.send_email(
            user=user, 
            to=request.to, 
            subject=request.subject, 
            body=request.body,
            cc=request.cc,
            bcc=request.bcc
        )
        return {"message": "Email sent successfully", "id": result['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_emails(
    user_id: str, 
    folder: str = "INBOX", 
    q: Optional[str] = None, 
    limit: int = 50, 
    skip: int = 0, 
    db: AsyncSession = Depends(get_db)
):
    """
    Lists processed emails with optional search and pagination.
    """
    # Optimized Query: Defer loading of heavy body text/html fields
    from sqlalchemy.orm import defer
    
    query = select(Email).filter(Email.user_id == user_id).order_by(Email.received_at.desc())
    query = query.options(defer(Email.body_text), defer(Email.body_html))
    
    # ... (Search and Filters kept same) ...
    # Search Filter
    if q:
        # Use Postgres Full Text Search (FTS)
        query = query.filter(Email.search_vector.op("@@")(func.plainto_tsquery("english", q)))

    # Handle Special folders (Labels)
    folder_upper = folder.upper()
    if folder_upper == 'STARRED':
        query = query.filter(Email.label_ids.contains('STARRED'))
    elif folder_upper == 'TRASH':
         query = query.filter(Email.label_ids.contains('TRASH'))
    elif folder_upper == 'SPAM':
         query = query.filter(Email.label_ids.contains('SPAM'))
    elif folder_upper == 'IMPORTANT':
         query = query.filter(Email.label_ids.contains('IMPORTANT'))
    else:
        if not q:
            query = query.filter(Email.folder == folder_upper)
            query = query.filter(~Email.label_ids.contains('TRASH'))
            query = query.filter(~Email.label_ids.contains('SPAM'))
        else:
             pass

    # Apply Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    emails = result.scalars().all()
    
    # Manual serialization to handle label_ids splitting safely
    serialized_emails = []
    for email in emails:
        # Basic dict conversion (simpler than Pydantic during debug)
        e_dict = {
            "id": str(email.id),
            "message_id": email.message_id,
            "thread_id": email.thread_id,
            "subject": email.subject,
            "sender": email.sender,
            "recipient": email.recipient,
            "snippet": email.snippet,
            # "body_text": email.body_text, # OMITTED for performance
            "received_at": email.received_at, # FastAPI/JSONResponse handles datetime
            "is_processed": email.is_processed,
            "event_title": email.event_title,
            "event_date": email.event_date,
            "deadline": email.deadline,
            "action_required": email.action_required,
            "priority": email.priority,
            "category": email.category,
            # Handle labels: Convert "LABEL1,LABEL2" -> ["LABEL1", "LABEL2"]
            "labelIds": email.label_ids.split(',') if email.label_ids else [] 
        }
        serialized_emails.append(e_dict)

    return serialized_emails

# AI Chat Endpoint - REMOVED

@router.post("/{message_id}/star")
async def star_email(message_id: str, user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        await gmail_service.modify_message(db, user, message_id, add_labels=['STARRED'])
        return {"message": "Email starred"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{message_id}/unstar")
async def unstar_email(message_id: str, user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        await gmail_service.modify_message(db, user, message_id, remove_labels=['STARRED'])
        return {"message": "Email unstarred"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{message_id}/trash")
async def trash_email(message_id: str, user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        await gmail_service.modify_message(db, user, message_id, add_labels=['TRASH'], remove_labels=['INBOX'])
        return {"message": "Email moved to trash"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{email_id}/dismiss_action")
async def dismiss_action(email_id: str, user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Dismisses the 'action required' flag for an email.
    """
    result = await db.execute(select(Email).filter(Email.id == email_id))
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    email.action_required = False
    await db.commit()
    return {"status": "success"}

@router.get("/{email_id}")
async def get_email_details(email_id: str, user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Fetches a single email by ID with full body content.
    """
    result = await db.execute(select(Email).filter(Email.id == email_id, Email.user_id == user_id))
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Return full details including body
    return {
        "id": str(email.id),
        "message_id": email.message_id,
        "thread_id": email.thread_id,
        "subject": email.subject,
        "sender": email.sender,
        "recipient": email.recipient,
        "snippet": email.snippet,
        "body_text": email.body_text, # Full body
        "body_html": email.body_html, # Full Html
        "received_at": email.received_at, 
        "is_processed": email.is_processed,
        "event_title": email.event_title,
        "event_date": email.event_date,
        "deadline": email.deadline,
        "action_required": email.action_required,
        "priority": email.priority,
        "category": email.category,
        "labelIds": email.label_ids.split(',') if email.label_ids else [] 
    }
