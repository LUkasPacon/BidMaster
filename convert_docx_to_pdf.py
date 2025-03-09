#!/usr/bin/env python3
"""
Skript pro konverzi DOCX na PDF.
"""
import sys
import os
from pathlib import Path
import argparse

def convert_docx_to_pdf(docx_path, pdf_path=None):
    """
    Konvertuje DOCX soubor na PDF.
    
    Args:
        docx_path: Cesta k DOCX souboru
        pdf_path: Cesta k výstupnímu PDF souboru (volitelné)
    
    Returns:
        str: Cesta k vytvořenému PDF souboru
    """
    try:
        # Pokud není zadána cesta k výstupnímu souboru, vytvoříme ji
        if pdf_path is None:
            pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
        
        # Kontrola, zda vstupní soubor existuje
        if not os.path.exists(docx_path):
            print(f"Soubor {docx_path} neexistuje!")
            return None
        
        # Kontrola, zda je vstupní soubor DOCX
        if not docx_path.lower().endswith(".docx"):
            print(f"Soubor {docx_path} není ve formátu DOCX!")
            return None
        
        # Pokus o import knihovny pro konverzi
        try:
            from docx2pdf import convert
            
            # Konverze DOCX na PDF
            print(f"Konvertuji {docx_path} na {pdf_path}...")
            convert(docx_path, pdf_path)
            
            # Kontrola, zda byl PDF soubor vytvořen
            if os.path.exists(pdf_path):
                print(f"Konverze dokončena. PDF soubor byl vytvořen: {pdf_path}")
                return pdf_path
            else:
                print(f"Konverze selhala. PDF soubor nebyl vytvořen.")
                return None
        except ImportError:
            print("Knihovna docx2pdf není nainstalována. Použijte 'pip3 install docx2pdf'.")
            return None
    except Exception as e:
        print(f"Chyba při konverzi: {e}")
        return None

def main():
    """
    Hlavní funkce pro spuštění konverze.
    """
    parser = argparse.ArgumentParser(description="Konverze DOCX na PDF")
    parser.add_argument("docx_path", help="Cesta k DOCX souboru")
    parser.add_argument("--pdf_path", help="Cesta k výstupnímu PDF souboru (volitelné)")
    
    args = parser.parse_args()
    
    convert_docx_to_pdf(args.docx_path, args.pdf_path)

if __name__ == "__main__":
    main() 