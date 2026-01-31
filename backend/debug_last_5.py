
import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.email import Email
from app.models.user import User # Required for relationship resolution

async def check_last_5():
    async with SessionLocal() as db:
        result = await db.execute(select(Email).order_by(Email.received_at.desc()).limit(5))
        emails = result.scalars().all()
        
        print(f"Found {len(emails)} emails:")
        for e in emails:
            print("-" * 40)
            print(f"Subject: {e.subject}")
            print(f"Snippet: {e.snippet}")
            print(f"Processed: {e.is_processed}")
            print(f"Event: {e.event_title} ({e.event_date})")
            print(f"Category: {e.category}")
            print(f"Action Required: {e.action_required}")

if __name__ == "__main__":
    asyncio.run(check_last_5())
