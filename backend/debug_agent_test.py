
import asyncio
import sys
from datetime import datetime
from app.services.agent_service import agent_service
from app.core.database import SessionLocal

async def test_agent(text):
    print(f"Testing Agent with text: {text}")
    received_at = datetime.utcnow()
    
    async with SessionLocal() as db:
        try:
            # We pass dummy user_id/sender just to satisfy the signature
            result = await agent_service.analyze_email(
                email_content=text,
                received_at=received_at,
                email_id="dummy_id",
                db=db,
                user_id="dummy_user",
                sender="test@example.com"
            )
            print("Analyze Result:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(test_agent(sys.argv[1]))
    else:
        print("Usage: python debug_agent_test.py '<text>'")
