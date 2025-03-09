#!/usr/bin/env python3
"""
Interaktivní průvodce pro BidMaster.
"""
import os
import sys
import argparse
from pathlib import Path
import subprocess
import time

# Přidání kořenového adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import get_config

config = get_config()

def clear_screen():
    """
    Vyčistí obrazovku.
    """
    if config.clear_screen:
        os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """
    Vytiskne hlavičku aplikace.
    """
    clear_screen()
    print("=" * 80)
    print(" " * 30 + "BidMaster" + " " * 30)
    print("=" * 80)
    print("Generátor obchodních nabídek pro implementaci MidPoint")
    print("-" * 80)
    print()

def print_menu(options):
    """
    Vytiskne menu s možnostmi.
    
    Args:
        options: Seznam možností
    """
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print()

def get_user_choice(options):
    """
    Získá volbu uživatele.
    
    Args:
        options: Seznam možností
        
    Returns:
        int: Index zvolené možnosti (0-based)
    """
    while True:
        try:
            choice = input("Zadejte číslo volby: ")
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print(f"Neplatná volba. Zadejte číslo od 1 do {len(options)}.")
        except ValueError:
            print("Neplatná volba. Zadejte číslo.")

def import_proposals_menu():
    """
    Menu pro import nabídek.
    """
    print_header()
    print("Import nabídek")
    print("-" * 80)
    print()
    
    options = [
        "Import z adresáře PDF souborů",
        "Import z adresáře DOCX souborů",
        "Import z adresáře JSON souborů",
        "Import z vlastního adresáře",
        "Zpět do hlavního menu"
    ]
    
    print_menu(options)
    choice = get_user_choice(options)
    
    if choice == 0:
        # Import z adresáře PDF souborů
        directory = "data/proposals/pdf"
        print(f"Importuji nabídky z adresáře {directory}...")
        subprocess.run(["python3", "manage_proposals.py", "import", directory])
        input("\nStiskněte Enter pro pokračování...")
        import_proposals_menu()
    elif choice == 1:
        # Import z adresáře DOCX souborů
        directory = "data/proposals/docx"
        print(f"Importuji nabídky z adresáře {directory}...")
        subprocess.run(["python3", "manage_proposals.py", "import", directory])
        input("\nStiskněte Enter pro pokračování...")
        import_proposals_menu()
    elif choice == 2:
        # Import z adresáře JSON souborů
        directory = "data/proposals/json"
        print(f"Importuji nabídky z adresáře {directory}...")
        subprocess.run(["python3", "manage_proposals.py", "import", directory])
        input("\nStiskněte Enter pro pokračování...")
        import_proposals_menu()
    elif choice == 3:
        # Import z vlastního adresáře
        directory = input("Zadejte cestu k adresáři s nabídkami: ")
        print(f"Importuji nabídky z adresáře {directory}...")
        subprocess.run(["python3", "manage_proposals.py", "import", directory])
        input("\nStiskněte Enter pro pokračování...")
        import_proposals_menu()
    elif choice == 4:
        # Zpět do hlavního menu
        main_menu()

def search_proposals_menu():
    """
    Menu pro vyhledávání nabídek.
    """
    print_header()
    print("Vyhledávání nabídek")
    print("-" * 80)
    print()
    
    query = input("Zadejte dotaz pro vyhledávání: ")
    limit = input("Zadejte maximální počet výsledků (výchozí: 5): ")
    
    if not limit:
        limit = "5"
    
    print(f"Vyhledávám nabídky podle dotazu: {query}...")
    subprocess.run(["python3", "manage_proposals.py", "search", query, "--limit", limit])
    
    input("\nStiskněte Enter pro pokračování...")
    main_menu()

def process_request_menu():
    """
    Menu pro zpracování poptávky.
    """
    print_header()
    print("Zpracování poptávky")
    print("-" * 80)
    print()
    
    print("Spouštím aplikaci pro zpracování poptávky...")
    subprocess.run(["python3", "run_cli.py"])
    
    input("\nStiskněte Enter pro pokračování...")
    main_menu()

def manage_database_menu():
    """
    Menu pro správu databáze.
    """
    print_header()
    print("Správa databáze")
    print("-" * 80)
    print()
    
    options = [
        "Zobrazit informace o konfiguraci",
        "Smazat všechny nabídky z databáze",
        "Zpět do hlavního menu"
    ]
    
    print_menu(options)
    choice = get_user_choice(options)
    
    if choice == 0:
        # Zobrazit informace o konfiguraci
        print("Zobrazuji informace o konfiguraci...")
        subprocess.run(["python3", "manage_proposals.py", "info"])
        input("\nStiskněte Enter pro pokračování...")
        manage_database_menu()
    elif choice == 1:
        # Smazat všechny nabídky z databáze
        print("VAROVÁNÍ: Tato akce smaže všechny nabídky z databáze!")
        confirm = input("Jste si jisti, že chcete pokračovat? (ano/ne): ")
        if confirm.lower() in ["ano", "a", "yes", "y"]:
            print("Mažu všechny nabídky z databáze...")
            subprocess.run(["python3", "manage_proposals.py", "delete"])
        input("\nStiskněte Enter pro pokračování...")
        manage_database_menu()
    elif choice == 2:
        # Zpět do hlavního menu
        main_menu()

def main_menu():
    """
    Hlavní menu aplikace.
    """
    print_header()
    
    options = [
        "Import nových nabídek",
        "Vyhledávání nabídek",
        "Zpracování poptávky",
        "Správa databáze",
        "Konec"
    ]
    
    print_menu(options)
    choice = get_user_choice(options)
    
    if choice == 0:
        # Import nových nabídek
        import_proposals_menu()
    elif choice == 1:
        # Vyhledávání nabídek
        search_proposals_menu()
    elif choice == 2:
        # Zpracování poptávky
        process_request_menu()
    elif choice == 3:
        # Správa databáze
        manage_database_menu()
    elif choice == 4:
        # Konec
        print("Děkujeme za použití aplikace BidMaster.")
        sys.exit(0)

def main():
    """
    Hlavní funkce aplikace.
    """
    parser = argparse.ArgumentParser(description="BidMaster - Interaktivní průvodce")
    parser.add_argument("--no-clear", action="store_true", help="Nezmazat obrazovku při spuštění")
    
    args = parser.parse_args()
    
    if args.no_clear:
        config.clear_screen = False
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nAplikace byla ukončena.")
        sys.exit(0)

if __name__ == "__main__":
    main() 