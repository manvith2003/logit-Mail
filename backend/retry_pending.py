import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from app.services.gmail_service import GmailService
from sqlalchemy import select, desc

async def retry_pending():
    service = GmailService()
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        
        # Get ALL unprocessed emails (limit 10)
        res = await db.execute(select(Email).filter(Email.user_id == user.id, Email.is_processed == False).limit(10))
        emails = res.scalars().all()
        
        if not emails:
            print("No pending emails to retry.")
            return

        print(f"Found {len(emails)} pending emails. Retrying...")
        ids = [str(e.id) for e in emails]
        
        # Call background task directly
        await service.process_emails_background(ids, str(user.id))
        print("Retry batch completed.")

if __name__ == "__main__":
    asyncio.run(retry_pending())
