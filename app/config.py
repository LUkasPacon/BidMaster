"""
Konfigurace aplikace.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Načtení proměnných prostředí z .env souboru
load_dotenv()

@dataclass
class Config:
    """
    Konfigurace aplikace.
    """
    # OpenAI API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    
    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "bidmaster")
    
    # Aplikace
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    clear_screen: bool = os.getenv("CLEAR_SCREEN", "True").lower() in ("true", "1", "t")

def get_config() -> Config:
    """
    Vrátí instanci konfigurace.
    
    Returns:
        Config: Instance konfigurace
    """
    return Config() 