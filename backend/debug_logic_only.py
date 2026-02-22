
import asyncio
from datetime import datetime, timedelta
# Mocking dependencies to import agent_service
import sys
from unittest.mock import MagicMock

# We need to import the class but we can't easily mock the LLM inside the class instantiation 
# if we import the instance. 
# However, the instance `agent_service` is already created in the file.
# We can just test the logic part by extracting it or subclassing.
# Easier: Just copy the logic snippet or import the internal method if possible.
# But `agent_service.analyze_email` does the parsing. I can mock the `self.llm.ainvoke`.

from app.services.agent_service import agent_service

async def test_logic_only():
    print("--- Testing Logic Only (Bypassing LLM) ---")
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.content = """
    {
        "status": "processed",
        "event_type": "deadline",
        "event_title": "Assignment",
        "date_text": "before next wednesday",
        "action": "auto_add"
    }
    """
    
    # Inject mock
    agent_service.llm = MagicMock()
    agent_service.llm.ainvoke.return_value = mock_response
    
    # Run
    received_at = datetime(2026, 2, 1) # Sunday
    print(f"Base Date: {received_at}")
    result = await agent_service.analyze_email("content ignored", received_at, "id")
    
    print("\nResult:")
    print(f"Resolved Date: {result.get('resolved_date')}")
    print(f"Original Text: {result.get('date_text')}")

if __name__ == "__main__":
    asyncio.run(test_logic_only())
