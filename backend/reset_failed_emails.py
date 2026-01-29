import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from sqlalchemy import select, desc

async def reset_emails():
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        
        # Find emails that are "Processed" but have no event result (potentially skipped due to error)
        # We only look at recent ones (last 5)
        res = await db.execute(select(Email).filter(
            Email.user_id == user.id, 
            Email.is_processed == True,
            Email.event_title == None,
            Email.category == "other" # Default category for failed/ignored
        ).order_by(desc(Email.received_at)).limit(5))
        
        emails = res.scalars().all()
        
        if not emails:
            print("No suspicious emails found.")
            return

        print(f"Found {len(emails)} potentially failed emails. Resetting...")
        for e in emails:
            print(f"Resetting: {e.subject} ({e.received_at})")
            e.is_processed = False
        
        await db.commit()
        print("Reset complete. They will be retried on next sync/retry loop.")

if __name__ == "__main__":
    asyncio.run(reset_emails())
