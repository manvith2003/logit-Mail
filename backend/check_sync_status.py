import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from sqlalchemy import select, desc

async def check_status():
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        if not user:
            print("❌ No user found.")
            return

        print(f"User: {user.email}")
        print(f"TimeStamp (The Stamp): {user.last_synced_at}")
        
        if user.last_synced_at:
            # Find the latest email
            res = await db.execute(select(Email).filter(Email.user_id == user.id).order_by(desc(Email.received_at)).limit(1))
            latest_email = res.scalars().first()
            
            if latest_email:
                print(f"Latest Email: '{latest_email.subject}'")
                print(f"Email Date : {latest_email.received_at}")
                
        else:
            print("⚠️ Status: Stamp is still NULL.")

if __name__ == "__main__":
    asyncio.run(check_status())
