from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from sqlalchemy import select
import asyncio

async def main():
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User))
        user = result.scalars().first()
        if not user:
            print("No User found!")
            return

        print(f"User ID: {user.id}")

        # Get Emails
        result = await db.execute(select(Email).filter(Email.user_id == user.id).limit(5))
        emails = result.scalars().all()
        
        print(f"Found {len(emails)} emails")
        for e in emails:
            print(f"ID: {e.id}, MsgID: {e.message_id}, Labels: {e.label_ids}, Subject: {e.subject}")

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        asyncio.run(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
