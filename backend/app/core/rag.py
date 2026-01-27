from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.core.config import settings
import chromadb
import os

# Initialize Google Gemini Embeddings
# We use the 'models/embedding-001' which is recommended for most text tasks
def get_embeddings():
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set")
    
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GOOGLE_API_KEY
    )

def get_vector_store():
    # Helper to get the ChromaDB persistent store
    persist_directory = "./chroma_db"
    
    # Ensure directory exists
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)

    embeddings = get_embeddings()
    
    # Initialize Chroma
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="email_embeddings"
    )
    
    return vector_store
