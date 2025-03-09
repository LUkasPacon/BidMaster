#!/usr/bin/env python3
"""
CLI aplikace pro generování nabídek.
"""
import os
import sys
import argparse
from pathlib import Path
import json
from typing import Dict, Any, Optional
import time

from app.chains.proposal_graph import (
    create_proposal_graph,
    init_proposal_state,
    process_user_input,
    Step
)
from app.utils.config import get_config

config = get_config()

def clear_screen():
    """Vyčistí obrazovku terminálu."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Vytiskne hlavičku aplikace."""
    print("=" * 80)
    print(" " * 30 + "BidMaster CLI" + " " * 30)
    print("=" * 80)
    print("Generátor obchodních nabídek pro implementaci MidPoint")
    print("-" * 80)

def print_chat_history(chat_history):
    """Vytiskne historii chatu."""
    for message in chat_history:
        if message["role"] == "user":
            print(f"\n👤 Vy: {message['content']}")
        else:
            print(f"\n🤖 Asistent: {message['content']}")

def main():
    """Hlavní funkce CLI aplikace."""
    parser = argparse.ArgumentParser(description="BidMaster CLI - Generátor obchodních nabídek")
    parser.add_argument(
        "--client-request", "-r",
        help="Cesta k souboru s poptávkou klienta"
    )
    parser.add_argument(
        "--client-name", "-n",
        help="Název klienta"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Zapne debug režim s podrobnějším výpisem"
    )
    parser.add_argument(
        "--no-clear", "-nc",
        action="store_true",
        help="Nezačíná s prázdnou obrazovkou po každém kroku"
    )
    args = parser.parse_args()

    # Nastavení debug režimu
    debug_mode = args.debug
    no_clear_mode = args.no_clear

    # Kontrola API klíčů
    if not config.openai_api_key:
        print("Chyba: Není nastaven OpenAI API klíč. Nastavte proměnnou prostředí OPENAI_API_KEY.")
        return 1
    
    if not config.pinecone_api_key or not config.pinecone_environment:
        print("Chyba: Nejsou nastaveny Pinecone API klíč nebo prostředí. Nastavte proměnné prostředí PINECONE_API_KEY a PINECONE_ENVIRONMENT.")
        return 1

    clear_screen()
    print_header()
    
    # Informace o použitém modelu
    print(f"\nPoužitý model: {config.model_name}")
    print(f"Embedding model: {config.embedding_model}")

    # Získání poptávky klienta
    client_request = ""
    if args.client_request:
        try:
            with open(args.client_request, "r", encoding="utf-8") as f:
                client_request = f.read()
            print(f"\nPoptávka načtena ze souboru: {args.client_request}")
        except Exception as e:
            print(f"Chyba při čtení souboru s poptávkou: {e}")
            return 1
    else:
        print("\nZadejte poptávku klienta (ukončete prázdným řádkem):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        client_request = "\n".join(lines)

    # Získání názvu klienta
    client_name = args.client_name if args.client_name else input("\nZadejte název klienta: ")

    if not client_request or not client_name:
        print("Chyba: Poptávka klienta a název klienta jsou povinné.")
        return 1

    # Vytvoření grafu
    print("\nInicializace grafu pro generování nabídek...")
    graph = create_proposal_graph()
    
    # Inicializace stavu
    state = init_proposal_state(client_request, client_name)
    
    # Spuštění prvního kroku (analýza poptávky)
    print("\nAnalýza poptávky klienta...")
    print("Prosím, počkejte...")
    
    try:
        # Animace načítání
        animation = "|/-\\"
        idx = 0
        start_time = time.time()
        
        # Spuštění grafu v samostatném vlákně
        import threading
        result = {"state": None, "error": None}
        
        def run_graph():
            try:
                result["state"] = graph.invoke(state)
            except Exception as e:
                result["error"] = e
        
        thread = threading.Thread(target=run_graph)
        thread.start()
        
        # Animace během zpracování
        while thread.is_alive():
            if not debug_mode:  # Animace pouze pokud není debug režim
                sys.stdout.write("\rZpracovávám " + animation[idx % len(animation)])
                sys.stdout.flush()
                idx += 1
            time.sleep(0.1)
        
        thread.join()
        
        # Kontrola výsledku
        if result["error"]:
            raise result["error"]
        
        state = result["state"]
        
        elapsed_time = time.time() - start_time
        print(f"\rAnalýza dokončena za {elapsed_time:.2f} sekund.")
    except Exception as e:
        print(f"\nChyba při analýze poptávky: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        return 1
    
    # Zobrazení výsledku analýzy
    if not no_clear_mode:
        clear_screen()
        print_header()
    print("\n=== Výsledek analýzy ===")
    print_chat_history(state["chat_history"])
    print("\n=== Konec analýzy ===")
    print("\nNyní můžete začít interaktivní konverzaci s asistentem.")
    print("Pro ukončení aplikace napište 'exit', 'quit' nebo 'konec'.")
    print("Pro přepnutí debug režimu napište 'debug'.")
    print("Pro vygenerování nabídky napište 'vytvoř nabídku' nebo 'pokračuj'.")
    
    # Interaktivní smyčka
    try:
        while state["current_step"] != "end":
            # Získání vstupu od uživatele
            user_input = input("\n👤 Vy: ")
            
            # Kontrola speciálních příkazů
            if user_input.lower() in ["exit", "quit", "konec"]:
                print("\nUkončuji aplikaci...")
                return 0
            
            if user_input.lower() == "debug":
                debug_mode = not debug_mode
                print(f"\nDebug režim {'zapnut' if debug_mode else 'vypnut'}")
                continue
                
            if user_input.lower() == "clear":
                no_clear_mode = False
                clear_screen()
                print_header()
                print_chat_history(state["chat_history"])
                continue
                
            if user_input.lower() == "no-clear":
                no_clear_mode = True
                print("\nRežim bez čištění obrazovky zapnut.")
                continue
            
            # Zpracování vstupu uživatele
            state = process_user_input(state, user_input)
            
            # Animace načítání během zpracování
            print("Zpracovávám odpověď...")
            animation = "|/-\\"
            idx = 0
            start_time = time.time()
            
            # Spuštění grafu v samostatném vlákně
            result = {"state": None, "error": None}
            
            def run_graph():
                try:
                    result["state"] = graph.invoke(state)
                except Exception as e:
                    result["error"] = e
            
            thread = threading.Thread(target=run_graph)
            thread.start()
            
            # Animace během zpracování
            while thread.is_alive():
                if not debug_mode:  # Animace pouze pokud není debug režim
                    sys.stdout.write("\rZpracovávám " + animation[idx % len(animation)])
                    sys.stdout.flush()
                    idx += 1
                time.sleep(0.1)
            
            thread.join()
            
            # Kontrola výsledku
            if result["error"]:
                print(f"\nChyba při zpracování: {result['error']}")
                if debug_mode:
                    import traceback
                    traceback.print_exc()
                # Pokračujeme i přes chybu
                continue
            
            state = result["state"]
            
            elapsed_time = time.time() - start_time
            if debug_mode:
                print(f"\rOdpověď zpracována za {elapsed_time:.2f} sekund.")
            
            # Zobrazení odpovědi
            if not no_clear_mode:
                clear_screen()
                print_header()
                print_chat_history(state["chat_history"])
            else:
                # Zobrazíme pouze poslední zprávu
                last_message = state["chat_history"][-1]
                if last_message["role"] == "assistant":
                    print(f"\n🤖 Asistent: {last_message['content']}")
            
            # Pokud byl vygenerován dokument, informujeme uživatele
            if state.get("document_path") and state["current_step"] == Step.HUMAN_FEEDBACK:
                print(f"\n📄 Dokument byl vygenerován a uložen na: {state['document_path']}")
                
                # Pokud je to možné, otevřeme dokument
                try:
                    if sys.platform == "darwin":  # macOS
                        os.system(f"open '{state['document_path']}'")
                    elif sys.platform == "win32":  # Windows
                        os.system(f'start "" "{state["document_path"]}"')
                    elif sys.platform == "linux":  # Linux
                        os.system(f"xdg-open '{state['document_path']}'")
                except Exception as e:
                    if debug_mode:
                        print(f"Nepodařilo se otevřít dokument: {e}")
    except KeyboardInterrupt:
        print("\nAplikace byla ukončena uživatelem.")
        return 0
    except Exception as e:
        print(f"\nNeočekávaná chyba: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        return 1
    
    # Konec
    if not no_clear_mode:
        clear_screen()
        print_header()
    print("\n✅ Generování nabídky bylo dokončeno.")
    print_chat_history(state["chat_history"])
    
    if state.get("document_path"):
        print(f"\n📄 Dokument byl vygenerován a uložen na: {state['document_path']}")
        print("\nMůžete dokument otevřít a prohlédnout si výslednou nabídku.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 