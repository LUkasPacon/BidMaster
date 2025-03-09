"""
Konfigurační utilita pro načítání proměnných prostředí.
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Načtení proměnných prostředí ze souboru .env
load_dotenv()

class Config(BaseModel):
    """Konfigurace aplikace."""
    
    # OpenAI API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "bidmaster-index")
    
    # LLM konfigurace
    model_name: str = os.getenv("MODEL_NAME", "gpt-4-turbo")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    
    # Konfigurace chunků pro RAG
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))

# Vytvoření instance konfigurace
config = Config()

def get_config() -> Config:
    """Vrátí instanci konfigurace."""
    return config 