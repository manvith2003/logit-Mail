import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from sqlalchemy import select, desc

async def check_latest():
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        if not user:
            print("❌ No user found.")
            return

        print(f"User: {user.email}")
        print(f"Sync Stamp: {user.last_synced_at}")
        
        # Latest Email
        res = await db.execute(select(Email).filter(Email.user_id == user.id).order_by(desc(Email.received_at)).limit(1))
        latest = res.scalars().first()
        
        if latest:
            print(f"Latest Email Subject: '{latest.subject}'")
            print(f"Snippet: {latest.snippet}")
            print(f"Received At: {latest.received_at}")
            print(f"Is Processed: {latest.is_processed}")
            print(f"AI Result: {latest.event_title} ({latest.event_date})")
            print(f"Reason/Category: {latest.category}")
        else:
            print("No emails in DB.")

if __name__ == "__main__":
    asyncio.run(check_latest())
