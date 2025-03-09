#!/usr/bin/env python3
"""
Testovací skript pro generování nabídky.
"""
import sys
import json
from pathlib import Path

# Přidání aktuálního adresáře do cesty pro import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.chains.proposal_graph import (
    create_proposal_graph,
    init_proposal_state,
    process_user_input,
    Step
)

def test_proposal_generation():
    """
    Testuje generování nabídky.
    """
    print("Inicializace grafu pro generování nabídek...")
    graph = create_proposal_graph()
    
    # Testovací poptávka
    client_request = """
    Dobrý den,
    
    jsme středně velká společnost působící v oblasti finančních služeb a hledáme řešení pro správu identit a přístupů (IAM) pro naše interní systémy. Po průzkumu trhu jsme se rozhodli pro implementaci řešení MidPoint.
    
    Naše společnost má přibližně 500 zaměstnanců a používáme následující systémy:
    - Active Directory pro správu uživatelů
    - Microsoft 365 pro e-maily a kancelářské aplikace
    - Interní CRM systém postavený na technologii Java
    - Účetní systém SAP
    - Několik webových aplikací pro interní použití
    
    Požadujeme:
    1. Implementaci MidPoint pro centrální správu identit
    2. Synchronizaci uživatelů s Active Directory
    3. Automatické zřizování a rušení účtů v Microsoft 365
    4. Napojení na interní CRM a SAP
    5. Implementaci workflow pro schvalování přístupů
    6. Základní reporting a audit
    
    Rádi bychom, aby implementace proběhla v průběhu následujících 3-6 měsíců. Rozpočet na projekt máme přibližně 1,5 milionu Kč.
    
    Prosím o zaslání nabídky s detailním popisem řešení, harmonogramem implementace a cenovou kalkulací.
    """
    
    client_name = "Testovací Klient, a.s."
    
    # Inicializace stavu
    state = init_proposal_state(client_request, client_name)
    
    # Spuštění prvního kroku (analýza poptávky)
    print("\nAnalýza poptávky klienta...")
    state = graph.invoke(state)
    
    # Zobrazení výsledku analýzy
    print("\n=== Výsledek analýzy ===")
    for message in state["chat_history"]:
        if message["role"] == "assistant":
            print(f"\nAsistent: {message['content']}")
    
    # Simulace odpovědi uživatele
    print("\nSimulace odpovědi uživatele: 'Vytvoř nabídku'")
    state = process_user_input(state, "Vytvoř nabídku")
    
    # Spuštění dalšího kroku
    print("\nGenerování nabídky...")
    state = graph.invoke(state)
    
    # Zobrazení výsledku
    print("\n=== Výsledek ===")
    print(f"Aktuální krok: {state['current_step']}")
    
    if state.get("document_path"):
        print(f"Dokument byl vytvořen a uložen na: {state['document_path']}")
    else:
        print("Dokument nebyl vytvořen.")
    
    # Zobrazení poslední zprávy
    if state["chat_history"]:
        last_message = state["chat_history"][-1]
        print(f"\nPoslední zpráva: {last_message['role']}: {last_message['content']}")
    
    return state

if __name__ == "__main__":
    test_proposal_generation() 