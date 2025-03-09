#!/usr/bin/env python3
"""
Testovací skript pro ověření funkčnosti importu PDF souborů.
"""
import sys
import os
from pathlib import Path

# Přidání kořenového adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.utils.import_proposals import (
    extract_text_from_pdf,
    extract_metadata_from_pdf,
    process_pdf_file
)

def test_pdf_extraction(pdf_path):
    """
    Testuje extrakci textu a metadat z PDF souboru.
    
    Args:
        pdf_path: Cesta k PDF souboru
    """
    print(f"Testování extrakce z PDF souboru: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"Soubor {pdf_path} neexistuje!")
        return
    
    # Extrakce textu
    print("\n=== Extrakce textu ===")
    text = extract_text_from_pdf(pdf_path)
    if text:
        # Zobrazíme jen prvních 500 znaků
        preview = text[:500]
        if len(text) > 500:
            preview += "..."
        print(f"Extrahovaný text (prvních 500 znaků):\n{preview}")
    else:
        print("Nepodařilo se extrahovat žádný text!")
    
    # Extrakce metadat
    print("\n=== Extrakce metadat ===")
    metadata = extract_metadata_from_pdf(pdf_path)
    for key, value in metadata.items():
        print(f"{key}: {value}")
    
    # Zpracování souboru
    print("\n=== Zpracování souboru ===")
    result = process_pdf_file(pdf_path)
    print(f"Délka extrahovaného textu: {len(result['text'])} znaků")
    print(f"Počet metadat: {len(result['metadata'])} položek")

def main():
    """
    Hlavní funkce pro spuštění testu.
    """
    if len(sys.argv) < 2:
        print("Použití: python3 test_pdf_import.py <cesta_k_pdf>")
        return
    
    pdf_path = sys.argv[1]
    test_pdf_extraction(pdf_path)

if __name__ == "__main__":
    main() 