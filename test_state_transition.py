#!/usr/bin/env python3
"""
Testovací skript pro testování přechodu mezi stavy.
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

def test_state_transition():
    """
    Testuje přechod mezi stavy.
    """
    print("Inicializace grafu pro generování nabídek...")
    graph = create_proposal_graph()
    
    # Testovací poptávka
    client_request = "Potřebujeme implementaci MidPoint pro 500 uživatelů."
    client_name = "Testovací Klient, a.s."
    
    # Inicializace stavu
    state = init_proposal_state(client_request, client_name)
    
    # Spuštění prvního kroku (analýza poptávky)
    print("\nAnalýza poptávky klienta...")
    state = graph.invoke(state)
    
    # Zobrazení aktuálního stavu
    print(f"\nAktuální stav po analýze: {state['current_step']}")
    
    # Simulace odpovědi uživatele
    print("\nSimulace odpovědi uživatele: 'Ano, to je správně.'")
    state = process_user_input(state, "Ano, to je správně.")
    
    # Spuštění dalšího kroku
    print("\nSpouštění dalšího kroku...")
    state = graph.invoke(state)
    
    # Zobrazení aktuálního stavu
    print(f"\nAktuální stav po odpovědi: {state['current_step']}")
    
    # Simulace příkazu k vytvoření nabídky
    print("\nSimulace příkazu k vytvoření nabídky: 'vytvoř nabídku'")
    state = process_user_input(state, "vytvoř nabídku")
    
    # Spuštění dalšího kroku
    print("\nSpouštění dalšího kroku...")
    state = graph.invoke(state)
    
    # Zobrazení aktuálního stavu
    print(f"\nAktuální stav po příkazu k vytvoření nabídky: {state['current_step']}")
    
    # Zobrazení poslední zprávy
    if state["chat_history"]:
        last_message = state["chat_history"][-1]
        print(f"\nPoslední zpráva: {last_message['role']}: {last_message['content']}")
    
    return state

if __name__ == "__main__":
    test_state_transition() 