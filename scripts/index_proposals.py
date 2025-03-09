#!/usr/bin/env python3
"""
Skript pro indexaci existujících nabídek do vektorové databáze.
"""
import os
import sys
import argparse
from pathlib import Path

# Přidání nadřazeného adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.document_processor import process_directory
from app.utils.vector_store import add_documents_to_vector_store, delete_all_vectors
from app.utils.config import get_config

def main():
    """
    Hlavní funkce skriptu.
    """
    parser = argparse.ArgumentParser(description="Indexace nabídek do vektorové databáze")
    parser.add_argument(
        "--directory", "-d", 
        default="data/proposals",
        help="Adresář s nabídkami (výchozí: data/proposals)"
    )
    parser.add_argument(
        "--reset", "-r", 
        action="store_true",
        help="Smazat existující vektory před indexací"
    )
    args = parser.parse_args()
    
    # Kontrola, zda adresář existuje
    if not os.path.exists(args.directory):
        print(f"Adresář {args.directory} neexistuje!")
        return 1
    
    # Smazání existujících vektorů, pokud je požadováno
    if args.reset:
        print("Mazání existujících vektorů...")
        delete_all_vectors()
    
    # Zpracování dokumentů
    print(f"Zpracování dokumentů z adresáře {args.directory}...")
    documents = process_directory(args.directory)
    
    if not documents:
        print("Nebyly nalezeny žádné dokumenty!")
        return 1
    
    print(f"Nalezeno {len(documents)} dokumentů.")
    
    # Přidání dokumentů do vektorové databáze
    print("Přidávání dokumentů do vektorové databáze...")
    add_documents_to_vector_store(documents)
    
    print("Indexace dokončena!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 