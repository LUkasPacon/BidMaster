"""Modul pro vyhledávání v návrzích."""
from typing import List, Optional
from langchain.schema import Document
import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
import pinecone

load_dotenv()

def init_pinecone():
    """Inicializace Pinecone."""
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY", ""),
        environment=os.getenv("PINECONE_ENV", "")
    )
    return PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX", "bidmaster"),
        namespace=os.getenv("PINECONE_NAMESPACE", "proposals")
    )

def search_proposals(query: str, limit: int = 5) -> List[Document]:
    """
    Vyhledá návrhy podle dotazu.
    
    Args:
        query: Vyhledávací dotaz
        limit: Maximální počet výsledků
        
    Returns:
        List[Document]: Seznam nalezených dokumentů
    """
    try:
        vectorstore = init_pinecone()
        results = vectorstore.similarity_search(query, k=limit)
        return results
    except Exception as e:
        print(f"Chyba při vyhledávání: {e}")
        return [] 