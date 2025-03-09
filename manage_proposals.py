#!/usr/bin/env python3
"""
Skript pro správu nabídek v BidMaster.
"""
import os
import sys
import argparse
from pathlib import Path

# Přidání kořenového adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.utils.import_proposals import import_proposals
from app.utils.vector_store import delete_all_vectors, similarity_search, get_embeddings
from app.config import get_config

config = get_config()

def import_cmd(args):
    """
    Importuje nabídky do vektorové databáze.
    
    Args:
        args: Argumenty příkazové řádky
    """
    import_proposals(args.directory, args.namespace)

def delete_cmd(args):
    """
    Smaže všechny vektory z vektorové databáze.
    
    Args:
        args: Argumenty příkazové řádky
    """
    print("Mazání všech vektorů z databáze...")
    delete_all_vectors()
    print("Všechny vektory byly smazány.")

def search_cmd(args):
    """
    Vyhledá podobné dokumenty ve vektorové databázi.
    
    Args:
        args: Argumenty příkazové řádky
    """
    print(f"Vyhledávání dokumentů podobných dotazu: '{args.query}'")
    documents = similarity_search(args.query, args.limit, args.namespace)
    
    if not documents:
        print("Nebyly nalezeny žádné podobné dokumenty.")
        return
    
    print(f"Nalezeno {len(documents)} podobných dokumentů:")
    for i, doc in enumerate(documents, 1):
        print(f"\n--- Dokument {i} ---")
        print(f"Zdroj: {doc.metadata.get('source', 'Neznámý')}")
        print(f"Klient: {doc.metadata.get('client_name', 'Neznámý')}")
        print(f"Datum: {doc.metadata.get('date', 'Neznámé')}")
        print(f"Verze: {doc.metadata.get('version', 'Neznámá')}")
        print("\nObsah:")
        # Zobrazíme jen prvních 500 znaků obsahu
        content = doc.page_content[:500]
        if len(doc.page_content) > 500:
            content += "..."
        print(content)

def info_cmd(args):
    """
    Zobrazí informace o konfiguraci.
    
    Args:
        args: Argumenty příkazové řádky
    """
    print("Informace o konfiguraci BidMaster:")
    print(f"Model: {config.model_name}")
    print(f"Embedding model: {config.embedding_model}")
    print(f"Pinecone index: {config.pinecone_index_name}")
    print(f"Pinecone environment: {config.pinecone_environment}")

def main():
    """
    Hlavní funkce pro spuštění správy nabídek.
    """
    parser = argparse.ArgumentParser(description="Správa nabídek v BidMaster")
    subparsers = parser.add_subparsers(dest="command", help="Příkaz")
    
    # Příkaz pro import nabídek
    import_parser = subparsers.add_parser("import", help="Import nabídek do vektorové databáze")
    import_parser.add_argument("directory", help="Cesta k adresáři s nabídkami")
    import_parser.add_argument("--namespace", help="Namespace pro vektorovou databázi", default=None)
    
    # Příkaz pro smazání všech vektorů
    delete_parser = subparsers.add_parser("delete", help="Smazání všech vektorů z vektorové databáze")
    
    # Příkaz pro vyhledávání
    search_parser = subparsers.add_parser("search", help="Vyhledávání podobných dokumentů")
    search_parser.add_argument("query", help="Dotaz pro vyhledávání")
    search_parser.add_argument("--limit", help="Maximální počet výsledků", type=int, default=5)
    search_parser.add_argument("--namespace", help="Namespace pro vyhledávání", default=None)
    
    # Příkaz pro zobrazení informací
    info_parser = subparsers.add_parser("info", help="Zobrazení informací o konfiguraci")
    
    args = parser.parse_args()
    
    if args.command == "import":
        import_cmd(args)
    elif args.command == "delete":
        delete_cmd(args)
    elif args.command == "search":
        search_cmd(args)
    elif args.command == "info":
        info_cmd(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 