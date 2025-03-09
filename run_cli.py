#!/usr/bin/env python3
"""
Hlavní skript pro spuštění CLI aplikace.
"""
import sys
import os
from pathlib import Path

# Přidání aktuálního adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.cli import main

if __name__ == "__main__":
    sys.exit(main()) 