import asyncio
from datetime import datetime
from app.services.agent_service import agent_service
import json

async def check_blank():
    print("--- Debugging Blank Subject ---")
    mock_now = datetime.now()
    # User's exact case
    text = "Subject: \nBody: Complete the assignment before Saturday"
    
    # Wait, the analyze_email takes `email_content`. 
    # In gmail_service, we prompt with: f"Subject: {email_subject}\n{email_body}"
    # So if subject is empty...
    
    input_text = "Subject: \nComplete the assignment before Saturday"
    # Let's check gmail_service.py to see default subject handling
    
    print(f"Input: '{input_text}'")
    
    # Call directly
    result = await agent_service.analyze_email(input_text, mock_now, "debug-blank-1")
    
    print("\n--- RAW RESULT ---")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(check_blank())
