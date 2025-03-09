#!/usr/bin/env python3
"""
Skript pro instalaci závislostí.
"""
import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """
    Nainstaluje závislosti z requirements.txt.
    """
    print("Instalace závislostí...")
    
    # Cesta k souboru requirements.txt
    requirements_path = Path(__file__).resolve().parent / "requirements.txt"
    
    if not requirements_path.exists():
        print(f"Soubor {requirements_path} neexistuje!")
        return 1
    
    # Instalace závislostí
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)], check=True)
        print("Závislosti byly úspěšně nainstalovány.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Chyba při instalaci závislostí: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(install_dependencies()) 