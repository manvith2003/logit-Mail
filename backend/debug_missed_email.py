import asyncio
from datetime import datetime
from app.services.agent_service import agent_service
import json

async def check_missed():
    print("--- Debugging Missed Email ---")
    mock_now = datetime.now()
    
    # Exact case from DB
    subject = "(No Subject)"
    body = "Submit assignment by tomorrow Kindly follow us..."
    input_text = f"Subject: {subject}\n{body}"
    
    print(f"Input: '{input_text}'")
    
    # Call directly
    result = await agent_service.analyze_email(input_text, mock_now, "debug-missed-1")
    
    print("\n--- RAW RESULT ---")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(check_missed())
