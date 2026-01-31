
import asyncio
import dateparser
from datetime import datetime, timedelta
from app.services.agent_service import agent_service
from app.core.database import SessionLocal

# Mock Time: Thursday, Jan 29, 2026
MOCK_NOW = datetime(2026, 1, 29, 10, 0, 0)

TEST_CASES = [
    # (Input Text, Expected Date String YYYY-MM-DD)
    ("Submit assignment by Friday", "2026-01-30"),
    ("Meeting tomorrow at 10am", "2026-01-30"),
    ("Project deadline on Jan 30th", "2026-01-30"),
    ("Complete report before end of this month", "2026-01-31"),
    ("Final submission end of next month", "2026-02-28"),
    ("Relax until end of weekend", "2026-02-01"), # Sunday
    ("Meeting next week Saturday", "2026-02-07"), # Manual +7 logic
    ("Submission due next Saturday", "2026-02-07"), # Ambiguous: Feb 7 (Next Week) or Jan 31 (This)? 
                                                    # dateparser often does Jan 31 for "Next Saturday"
                                                    # Let's see what happens.
    ("Homework due Saturday", "2026-01-31")       # This coming Saturday
]

async def run_tests():
    print(f"Running Regression Suite at Mock Time: {MOCK_NOW}")
    print("="*60)
    
    passed = 0
    failed = 0
    
    async with SessionLocal() as db:
        for text, expected_date_str in TEST_CASES:
            print(f"Testing: '{text}'...")
            try:
                # We interpret expected string to date object for comparison
                expected_date = datetime.strptime(expected_date_str, "%Y-%m-%d").date()
                
                result = await agent_service.analyze_email(
                    email_content=text,
                    received_at=MOCK_NOW, # Inject mock time
                    email_id="test",
                    db=db,
                    user_id="test_user",
                    sender="test@example.com"
                )
                
                if not result:
                    print(f"  FAILED: Agent returned None")
                    failed += 1
                    continue
                    
                actual_iso = result.get('resolved_date')
                if not actual_iso:
                     print(f"  FAILED: No date resolved. Result: {result}")
                     failed += 1
                     continue
                     
                actual_date = datetime.fromisoformat(actual_iso).date()
                
                if actual_date == expected_date:
                    print(f"  PASS ✅ ({actual_date})")
                    passed += 1
                else:
                    print(f"  FAIL ❌ Expected {expected_date}, Got {actual_date}")
                    failed += 1
                    
            except Exception as e:
                print(f"  CRASH 💥: {e}")
                failed += 1
            print("-" * 60)

    print(f"\nFinal Results: {passed}/{len(TEST_CASES)} Passed.")

if __name__ == "__main__":
    asyncio.run(run_tests())
