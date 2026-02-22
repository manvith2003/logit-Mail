
import asyncio
import os
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv(dotenv_path=".env")

from app.services.agent_service import agent_service
from datetime import datetime

async def run_test():
    email_content = "Assignment should be completed before next wednesday"
    # Simulate today as Sunday, Feb 1st 2026
    received_at = datetime(2026, 2, 1)
    
    print(f"--- Debugging Full Pipeline for: '{email_content}' ---")
    print(f"Received At: {received_at}")
    
    result = await agent_service.analyze_email(
        email_content=email_content,
        received_at=received_at,
        email_id="debug-123"
    )
    
    print("\n--- Result ---")
    if result:
        print(f"Status: {result.get('status')}")
        print(f"Event Type: {result.get('event_type')}")
        print(f"Date Text (from LLM): '{result.get('date_text')}'")
        print(f"Resolved Date: {result.get('resolved_date')}")
        print(f"Action: {result.get('action')}")
        print(f"Reason: {result.get('reason')}")
    else:
        print("Result is None")

if __name__ == "__main__":
    asyncio.run(run_test())
