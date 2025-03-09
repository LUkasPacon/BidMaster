"""
Utilita pro zpracování dokumentů.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    # Zkusíme importovat z langchain_community
    from langchain_community.document_loaders import (
        PyPDFLoader,
        Docx2txtLoader,
        UnstructuredFileLoader,
        TextLoader
    )
except ImportError:
    # Pokud to nefunguje, zkusíme starší způsob importu
    from langchain.document_loaders import (
        PyPDFLoader,
        Docx2txtLoader,
        UnstructuredFileLoader,
        TextLoader
    )
    
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.utils.config import get_config

config = get_config()

def load_document(file_path: str) -> List[Document]:
    """
    Načte dokument podle přípony souboru.
    
    Args:
        file_path: Cesta k souboru
        
    Returns:
        List[Document]: Seznam dokumentů
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_extension in [".docx", ".doc"]:
            loader = Docx2txtLoader(file_path)
        elif file_extension == ".txt":
            loader = TextLoader(file_path)
        else:
            # Pro ostatní typy souborů použijeme obecný loader
            loader = UnstructuredFileLoader(file_path)
            
        return loader.load()
    except Exception as e:
        print(f"Chyba při načítání dokumentu {file_path}: {e}")
        return []

def split_documents(documents: List[Document]) -> List[Document]:
    """
    Rozdělí dokumenty na menší části pro lepší zpracování.
    
    Args:
        documents: Seznam dokumentů
        
    Returns:
        List[Document]: Seznam rozdělených dokumentů
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        length_function=len,
    )
    
    return text_splitter.split_documents(documents)

def process_document(file_path: str) -> List[Document]:
    """
    Načte a zpracuje dokument.
    
    Args:
        file_path: Cesta k souboru
        
    Returns:
        List[Document]: Seznam zpracovaných dokumentů
    """
    documents = load_document(file_path)
    if not documents:
        return []
    
    return split_documents(documents)

def process_directory(directory_path: str) -> List[Document]:
    """
    Zpracuje všechny dokumenty v adresáři.
    
    Args:
        directory_path: Cesta k adresáři
        
    Returns:
        List[Document]: Seznam zpracovaných dokumentů
    """
    all_documents = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.startswith('.'):  # Přeskočit skryté soubory
                continue
                
            file_path = os.path.join(root, file)
            documents = process_document(file_path)
            
            # Přidáme metadata o původním souboru
            for doc in documents:
                doc.metadata["source_file"] = file_path
                
            all_documents.extend(documents)
            
    return all_documents 