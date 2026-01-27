import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select

# Define Minimal Model to match table
from sqlalchemy import Column, String, Boolean, UUID, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    id = Column(UUID(as_uuid=True), primary_key=True)
    message_id = Column(String)
    label_ids = Column(String)
    subject = Column(String)
    user_id = Column(UUID(as_uuid=True))

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/magic_mail"

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("Connected to DB")
        # List all emails and their labels
        result = await session.execute(select(Email).limit(10))
        emails = result.scalars().all()
        
        print(f"Found {len(emails)} emails")
        for e in emails:
            print(f"MSG_ID: {e.message_id} | LABELS: {e.label_ids} | SUBJECT: {e.subject}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
