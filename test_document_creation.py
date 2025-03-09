#!/usr/bin/env python3
"""
Testovací skript pro vytvoření dokumentu.
"""
import sys
import json
from pathlib import Path

# Přidání aktuálního adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.utils.docx_generator import create_proposal_document

def test_document_creation():
    """
    Testuje vytvoření dokumentu.
    """
    print("Začínám test vytvoření dokumentu...")
    
    # Testovací data pro nabídku
    proposal_data = {
        "client_name": "Testovací Klient, a.s.",
        "introduction": "Vážený pane Nováku, děkujeme za Váš zájem o implementaci řešení MidPoint pro správu identit a přístupů (IAM) ve Vaší společnosti.",
        "solution_description": "Navrhované řešení MidPoint bude implementováno jako centrální bod pro správu identit a přístupů ve Vaší organizaci.",
        "scope_of_work": "Implementace zahrnuje následující práce: instalace a konfigurace MidPoint, integrace s Active Directory, implementace workflow pro schvalování přístupů.",
        "timeline": "Implementace bude probíhat v následujících fázích: analýza (2 týdny), implementace (8 týdnů), testování (2 týdny), nasazení (2 týdny).",
        "pricing": "Celková cena implementace je 1 200 000 Kč bez DPH.",
        "contact_info": "Pro další informace nás kontaktujte na info@example.com nebo na telefonu +420 123 456 789."
    }
    
    # Vytvoření dokumentu
    print("\nVytvářím dokument...")
    document_path = create_proposal_document(proposal_data)
    
    # Zobrazení výsledku
    if document_path and document_path != "Chyba při ukládání dokumentu":
        print(f"\nDokument byl úspěšně vytvořen a uložen na: {document_path}")
    else:
        print("\nChyba při vytváření dokumentu.")
    
    return document_path

if __name__ == "__main__":
    test_document_creation() 