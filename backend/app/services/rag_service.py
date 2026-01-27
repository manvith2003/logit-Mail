from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.config import settings
from app.core.rag import get_vector_store
import json

# Define the extracted data structure
class EmailExtraction(BaseModel):
    event_title: Optional[str] = Field(description="The title of the event or main subject found in the email, or None")
    event_date: Optional[str] = Field(description="The date of the event in ISO format (YYYY-MM-DD HH:MM:SS), or None")
    deadline: Optional[str] = Field(description="Any deadline mentioned in the email in ISO format, or None")
    action_required: bool = Field(description="True if the email requires user action or reply")

def get_llm():
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing")
    
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )

async def process_email_content(email_text: str):
    """
    Extracts structured data from email text using Gemini.
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=EmailExtraction)
    
    prompt = PromptTemplate(
        template="""
        You are an AI assistant processing emails.
        Extract the following information from the email text below.
        If a date is relative (e.g. "next Friday"), calculate it assuming today is {current_date}.
        
        {format_instructions}
        
        Email Content:
        {email_text}
        """,
        input_variables=["email_text", "current_date"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        current_date = datetime.now().isoformat()
        result = await chain.ainvoke({"email_text": email_text[:4000], "current_date": current_date}) # Summarize/Turncate if too long
        return result
    except Exception as e:
        print(f"Error extracting data from email: {e}")
        return None

def embed_email(email_id: str, email_text: str, user_id: str):
    """
    Stores email text in ChromaDB for future RAG search.
    """
    try:
        vector_store = get_vector_store()
        # Add text to vector store
        vector_store.add_texts(
            texts=[email_text],
            metadatas=[{"email_id": email_id, "user_id": user_id}],
            ids=[email_id]
        )
        print(f"Embedded email {email_id} for user {user_id}")
    except Exception as e:
        print(f"Error embedding email {email_id}: {e}")
