
import asyncio
import sys
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.email import Email
from app.models.user import User

async def reset_email(subject_part):
    async with SessionLocal() as db:
        result = await db.execute(select(Email).filter(Email.subject.ilike(f"%{subject_part}%")))
        emails = result.scalars().all()
        
        if not emails:
            print(f"No emails found matching '{subject_part}'")
            return

        print(f"Found {len(emails)} emails. Resetting...")
        for e in emails:
            print(f"Resetting: {e.subject}")
            e.is_processed = False
            e.action_required = False
            e.event_title = None
            e.event_date = None
        
        await db.commit()
        print("Done.")

if __name__ == "__main__":
    subject = "Assignment"
    if len(sys.argv) > 1:
        subject = sys.argv[1]
    asyncio.run(reset_email(subject))
