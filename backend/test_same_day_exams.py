
import asyncio
from datetime import datetime
from app.services.agent_service import agent_service
from app.core.database import SessionLocal

# Mock Time: Feb 1, 2026
MOCK_NOW = datetime(2026, 2, 1, 10, 0, 0)

# Simulated Email: Two exams on Feb 10th
MOCK_EMAIL_BODY = """
Here is your schedule:

[Attachment PDF Content]:
DATE: Feb 10th, 2026
1. Mathematics - 10:00 AM
2. Physics     - 02:00 PM
-------------------------
"""

async def run_test():
    print(f"Simulating Same-Day Exams Test at Mock Time: {MOCK_NOW}")
    print("="*60)
    print(MOCK_EMAIL_BODY)
    print("="*60)
    
    async with SessionLocal() as db:
        try:
            result = await agent_service.analyze_email(
                email_content=MOCK_EMAIL_BODY,
                received_at=MOCK_NOW,
                email_id="same_day_test_id",
                db=db,
                user_id="test_user",
                sender="university@example.com"
            )
            
            print("\nAI Result:")
            print(result)
            
            if result and result.get('event_title'):
                print(f"\n✅ Result Title: {result['event_title']}")
                print(f"✅ Result Date: {result['date_text']}")
                
                # Check for combination
                title = result['event_title'].lower()
                if "math" in title and "physics" in title:
                    print("✅ SUCCESS: Combined both exams into title!")
                elif "2 exams" in title:
                    print("✅ SUCCESS: Recognized count!")
                else:
                    print("⚠️ WARNING: Might have only picked one. Check output.")
            else:
                print("❌ FAILED to detect event.")
                
        except Exception as e:
            print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
