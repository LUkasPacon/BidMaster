#!/usr/bin/env python3
"""
Skript pro nastavení projektu.
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_project():
    """
    Nastaví projekt - vytvoří potřebné adresáře a šablony.
    """
    print("Nastavení projektu BidMaster...")
    
    # Vytvoření adresářů
    directories = [
        "data/proposals",
        "data/templates",
        "data/generated",
        "data/examples/proposals"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Vytvořen adresář: {directory}")
    
    # Vytvoření šablony
    try:
        subprocess.run([sys.executable, "scripts/create_template.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Chyba při vytváření šablony: {e}")
    
    # Kopírování vzorových souborů
    try:
        if Path("data/examples/poptavka_vzor.txt").exists():
            Path("data/examples/poptavka_vzor.txt").rename("data/proposals/poptavka_vzor.txt")
            print("Zkopírována vzorová poptávka do data/proposals/")
        
        if Path("data/examples/proposals/nabidka_vzor.txt").exists():
            Path("data/examples/proposals/nabidka_vzor.txt").rename("data/proposals/nabidka_vzor.txt")
            print("Zkopírována vzorová nabídka do data/proposals/")
    except Exception as e:
        print(f"Chyba při kopírování vzorových souborů: {e}")
    
    # Vytvoření .env souboru, pokud neexistuje
    if not Path(".env").exists():
        try:
            with open(".env.example", "r", encoding="utf-8") as example_file:
                example_content = example_file.read()
            
            with open(".env", "w", encoding="utf-8") as env_file:
                env_file.write(example_content)
            
            print("Vytvořen soubor .env ze šablony .env.example")
            print("DŮLEŽITÉ: Upravte soubor .env a nastavte správné hodnoty API klíčů!")
        except Exception as e:
            print(f"Chyba při vytváření .env souboru: {e}")
    
    print("\nNastavení projektu dokončeno!")
    print("\nDalší kroky:")
    print("1. Upravte soubor .env a nastavte správné hodnoty API klíčů")
    print("2. Umístěte existující nabídky do složky data/proposals/")
    print("3. Spusťte indexaci nabídek: python3 scripts/index_proposals.py")
    print("4. Spusťte aplikaci: python3 run_cli.py")

if __name__ == "__main__":
    setup_project() 