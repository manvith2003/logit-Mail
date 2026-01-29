import asyncio
from datetime import datetime, timedelta
from app.services.agent_service import agent_service
import json

async def test_date_logic():
    # Mock "Current" time: Let's assume today is Monday, Jan 26, 2026 for simulation
    # effectively verifying relative logic
    mock_received_at = datetime.now()
    
    print(f"--- Testing Date Resolution Logic ---")
    print(f"Reference Date (Simulated 'Now'): {mock_received_at.date()}")
    
    # Mock Email Content with RELATIVE DATE and EXAM type
    email_content = """
    Hi Manvith,
    
    Just a reminder that the Advanced Algorithms Exam is scheduled for next Friday at 2:00 PM.
    Please prepare accordingly.
    
    Best,
    Prof. Smith
    """
    
    print(f"\nEmail Content Snippet: '...Algorithms Exam is scheduled for next Friday at 2:00 PM...'")
    
    # Run Agent
    print("\nRunning Agent Analysis...")
    result = await agent_service.analyze_email(
        email_content=email_content,
        received_at=mock_received_at, # "next Friday" should be calculated relative to this
        email_id="test-mock-id-123"
    )
    
    if not result:
        print("Agent returned None (Error)")
        return

    print("\n--- Agent Result ---")
    print(f"Event Type: {result.get('event_type')} (Expected: exam)")
    print(f"Extracted Date Text: '{result.get('date_text')}'")
    print(f"Resolved ISO Date: {result.get('resolved_date')}")
    
    payload = result.get('calendar_event_payload', {})
    reminders = payload.get('reminders', {}).get('overrides', [])
    print(f"Reminders Set: {json.dumps(reminders, indent=2)}")
    
    # Verification Logic
    if result.get('resolved_date'):
         print("\n✅ Date Persing Successful!")
    else:
         print("\n❌ Date Parsing Failed.")

    if any(r['minutes'] == 2880 for r in reminders): # 2 * 24 * 60 = 2880
         print("✅ Exam Rule Applied (2 Days Reminder).")
    else:
         print("❌ Exam Rule Failed.")

if __name__ == "__main__":
    asyncio.run(test_date_logic())
