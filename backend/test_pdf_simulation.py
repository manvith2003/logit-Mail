
import asyncio
from datetime import datetime
from app.services.agent_service import agent_service
from app.core.database import SessionLocal

# Mock Time: Feb 1, 2026
MOCK_NOW = datetime(2026, 2, 1, 10, 0, 0)

# Simulated Email Body + PDF Content
MOCK_EMAIL_BODY = """
Hi, please find the attached exam schedule for the semester.
Good luck!

[Attachment PDF Content]:
FINAL EXAM SCHEDULE 2026
-------------------------
1. Mathematics - Feb 10th, 2026 (10:00 AM) - Room 101
2. Physics     - Feb 12th, 2026 (2:00 PM)  - Room 102
3. Chemistry   - Feb 15th, 2026 (10:00 AM) - Room 103
-------------------------
"""

async def run_test():
    print(f"Simulating PDF Extraction Test at Mock Time: {MOCK_NOW}")
    print("="*60)
    print(MOCK_EMAIL_BODY)
    print("="*60)
    
    async with SessionLocal() as db:
        try:
            result = await agent_service.analyze_email(
                email_content=MOCK_EMAIL_BODY,
                received_at=MOCK_NOW,
                email_id="pdf_test_id",
                db=db,
                user_id="test_user",
                sender="university@example.com"
            )
            
            print("\nAI Result:")
            print(result)
            
            if result and result.get('event_title'):
                print(f"\n✅ Detected Event: {result['event_title']} on {result['date_text']}")
                
                # Check if it picked the FIRST one (Math - Feb 10)
                if "Feb 10" in result['date_text'] or "Math" in result['event_title']:
                    print("✅ CORRECTLY picked the FIRST/NEXT exam!")
                else:
                    print("⚠️ WARNING: Did not pick the first exam. Check output.")
            else:
                print("❌ FAILED to detect event.")
                
        except Exception as e:
            print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
