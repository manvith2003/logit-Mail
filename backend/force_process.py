import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from app.services.gmail_service import GmailService
from sqlalchemy import select, desc

async def force_process():
    service = GmailService()
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        
        # Get unprocessed email
        res = await db.execute(select(Email).filter(Email.user_id == user.id, Email.is_processed == False).order_by(desc(Email.received_at)).limit(1))
        email = res.scalars().first()
        
        if not email:
            print("No unprocessed emails found.")
            return

        print(f"Force processing email: {email.subject} (ID: {email.id})")
        
        # Call background task directly (await it)
        await service.process_emails_background([str(email.id)], str(user.id))
        
        # Check result
        await db.refresh(email)
        print(f"Post-Process Status: {email.is_processed}")
        print(f"AI Result: event_title='{email.event_title}'")

if __name__ == "__main__":
    asyncio.run(force_process())
