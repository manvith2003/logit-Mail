import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.email import Email
from sqlalchemy import select, desc
from datetime import datetime

async def fix_stamp():
    async with SessionLocal() as db:
        # Get User
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        if not user:
            print("❌ No user found.")
            return

        print(f"User: {user.email}")
        print(f"Current Stamp: {user.last_synced_at}")
        
        # Build logic: Get latest email OR just use NOW if database is empty or user wants strict cutoff
        # User said "put stamp at the latest mail"
        res = await db.execute(select(Email).filter(Email.user_id == user.id).order_by(desc(Email.received_at)).limit(1))
        latest = res.scalars().first()
        
        new_stamp = datetime.utcnow()
        if latest:
             print(f"Latest Email: {latest.subject} ({latest.received_at})")
             # We set stamp to NOW to be safe (ignore everything present), 
             # Or set to latest.received_at? 
             # "put stamp at the latest mail" -> let's use latest.received_at
             new_stamp = latest.received_at
        
        user.last_synced_at = new_stamp
        db.add(user)
        await db.commit()
        
        print(f"✅ UPDATED Stamp to: {user.last_synced_at}")
        print("Existing emails should now be ignored by future syncs.")

if __name__ == "__main__":
    asyncio.run(fix_stamp())
