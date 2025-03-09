#!/usr/bin/env python3
"""
Testovací skript pro import nabídek.
"""
import sys
from pathlib import Path

# Přidání kořenového adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from app.utils.import_proposals import import_proposals
    print("Import funkce import_proposals úspěšný")
except ImportError as e:
    print(f"Chyba při importu funkce import_proposals: {e}")
    sys.exit(1)

try:
    from app.utils.vector_store import delete_all_vectors, similarity_search
    print("Import funkcí delete_all_vectors a similarity_search úspěšný")
except ImportError as e:
    print(f"Chyba při importu funkcí delete_all_vectors a similarity_search: {e}")
    sys.exit(1)

try:
    from app.config import get_config
    config = get_config()
    print("Import konfigurace úspěšný")
except ImportError as e:
    print(f"Chyba při importu konfigurace: {e}")
    sys.exit(1)

def main():
    """
    Hlavní funkce pro testování importu.
    """
    if len(sys.argv) < 2:
        print("Použití: python3 test_import.py <cesta_k_adresáři>")
        return
    
    directory_path = sys.argv[1]
    print(f"Testování importu nabídek z adresáře {directory_path}...")
    
    try:
        import_proposals(directory_path)
        print("Import nabídek úspěšný")
    except Exception as e:
        print(f"Chyba při importu nabídek: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 