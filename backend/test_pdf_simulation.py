import asyncio
import os
from datetime import datetime
# Set env var for testing if not set
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "dummy") 

# Mock settings if needed, or rely on app.core.config
# We need to make sure we can import app.services.agent_service
import sys
sys.path.append(os.getcwd())

from app.services.agent_service import agent_service

async def test_same_day_events():
    print("--- Testing Same Day Events (PDF Simulation) ---")
    
    # Simulate text extracted from a PDF
    pdf_text = """
    [Attachment PDF Content]:
    Exam Schedule
    
    Date: October 25, 2025
    10:00 AM - Mathematics
    02:00 PM - Physics
    
    Date: October 26, 2025
    10:00 AM - Chemistry
    """
    
    email_content = f"Please find the attached exam schedule.\n\n{pdf_text}"
    received_at = datetime(2025, 10, 1)
    
    print(f"Input Content:\n{email_content}\n")
    
    if not agent_service.llm:
        print("Skipping test: LLM not initialized (missing API key?)")
        return

    try:
        result = await agent_service.analyze_email(
            email_content=email_content,
            received_at=received_at,
            email_id="test_pdf_1"
        )
        
        print("\nResult:")
        import json
        print(json.dumps(result, indent=2))
        
        # Verification Logic
        if result and result.get("event_type") == "exam":
            title = result.get("event_title", "").lower()
            if "math" in title and "physics" in title:
                print("\n✅ SUCCESS: Detected both exams on same day.")
            else:
                print("\n❌ FAILURE: Did not combine events. Title:", result.get("event_title"))
        else:
             print("\n❌ FAILURE: Event not detected or wrong type.")
             
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_same_day_events())
