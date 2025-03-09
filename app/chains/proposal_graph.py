"""
LangGraph komponenta pro interaktivní generování nabídek.
"""
from typing import Dict, Any, List, Tuple, Annotated, TypedDict, Optional
from enum import Enum
import json
import operator
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Definice konstant pro END
END = "end"

from app.utils.config import get_config
from app.utils.vector_store import similarity_search
from app.utils.docx_generator import create_proposal_document

config = get_config()

# Definice stavů grafu
class ProposalState(TypedDict):
    """Stav grafu pro generování nabídek."""
    
    # Vstupní data
    client_request: str
    client_name: str
    
    # Stav zpracování
    current_step: str
    chat_history: List[Dict[str, Any]]
    
    # Shromážděná data
    collected_data: Dict[str, Any]
    
    # Výstupní data
    proposal_data: Optional[Dict[str, Any]]
    document_path: Optional[str]
    
    # Počítadlo kroků pro prevenci nekonečné rekurze
    step_counter: Dict[str, int]

# Definice kroků
class Step(str, Enum):
    """Kroky v procesu generování nabídky."""
    
    ANALYZE_REQUEST = "analyze_request"
    GATHER_INFORMATION = "gather_information"
    GENERATE_PROPOSAL = "generate_proposal"
    CREATE_DOCUMENT = "create_document"
    HUMAN_FEEDBACK = "human_feedback"
    END = "end"  # Explicitní konec

# Funkce pro analýzu poptávky
def analyze_request(state: ProposalState) -> ProposalState:
    """
    Analyzuje poptávku klienta a identifikuje chybějící informace.
    
    Args:
        state: Aktuální stav
        
    Returns:
        ProposalState: Aktualizovaný stav
    """
    # Vytvoření LLM
    llm = ChatOpenAI(
        model=config.model_name,
        temperature=0.2,
        openai_api_key=config.openai_api_key
    )
    
    # Získání relevantního kontextu
    context = similarity_search(state["client_request"], k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in context]) if context else "Nebyly nalezeny žádné relevantní dokumenty."
    
    # Vytvoření zpráv pro prompt
    system_message = SystemMessage(content="""
    Jsi asistent pro analýzu poptávek na implementaci produktu MidPoint.
    Tvým úkolem je analyzovat poptávku klienta a identifikovat chybějící informace, které jsou potřeba pro vytvoření kvalitní nabídky.
    
    Zaměř se na následující oblasti:
    1. Rozsah implementace - jaké moduly a funkce MidPoint klient požaduje
    2. Časový rámec - kdy klient očekává dokončení implementace
    3. Integrace - s jakými systémy má být MidPoint integrován
    4. Specifické požadavky - jaké má klient specifické požadavky na implementaci
    5. Rozpočet - jaký má klient rozpočet na implementaci
    
    Odpověz ve dvou částech:
    1. Shrnutí poptávky - co víme z poptávky klienta
    2. Chybějící informace - jaké informace chybí pro vytvoření kvalitní nabídky
    """)
    
    human_message = HumanMessage(content=f"""
    Poptávka klienta:
    {state["client_request"]}
    
    Název klienta: {state["client_name"]}
    
    Relevantní kontext z předchozích nabídek:
    {context_text}
    """)
    
    # Generování analýzy
    response = llm.invoke([system_message, human_message])
    
    # Aktualizace stavu
    new_state = state.copy()
    new_state["chat_history"] = state.get("chat_history", []) + [
        {"role": "assistant", "content": response.content}
    ]
    new_state["current_step"] = Step.GATHER_INFORMATION
    
    # Aktualizace počítadla kroků
    step_counter = new_state.get("step_counter", {})
    step_counter[Step.ANALYZE_REQUEST] = step_counter.get(Step.ANALYZE_REQUEST, 0) + 1
    new_state["step_counter"] = step_counter
    
    return new_state

# Funkce pro sběr informací
def gather_information(state: ProposalState) -> ProposalState:
    """
    Sbírá informace od uživatele.
    
    Args:
        state: Aktuální stav
        
    Returns:
        ProposalState: Aktualizovaný stav
    """
    # Aktualizace stavu
    new_state = state.copy()
    
    # Aktualizace počítadla kroků
    step_counter = new_state.get("step_counter", {})
    step_counter[Step.GATHER_INFORMATION] = step_counter.get(Step.GATHER_INFORMATION, 0) + 1
    new_state["step_counter"] = step_counter
    
    # Kontrola počtu opakování - prevence nekonečné rekurze
    if step_counter.get(Step.GATHER_INFORMATION, 0) > 20:
        new_state["current_step"] = Step.GENERATE_PROPOSAL
        new_state["chat_history"] = state.get("chat_history", []) + [
            {"role": "assistant", "content": "Dosáhli jsme maximálního počtu kroků pro sběr informací. Přecházím k vytvoření nabídky s dostupnými informacemi."}
        ]
        return new_state
    
    # Pokud máme poslední zprávu od uživatele, zpracujeme ji
    chat_history = state.get("chat_history", [])
    if chat_history and chat_history[-1]["role"] == "user":
        # Kontrola, zda uživatel chce přejít k vytvoření nabídky
        last_message = chat_history[-1]["content"].lower().strip()
        
        # Seznam frází, které indikují přechod k vytvoření nabídky
        trigger_phrases = [
            "vytvoř nabídku", "generuj nabídku", "vytvor nabidku", 
            "vygeneruj nabídku", "udělej nabídku", "připrav nabídku",
            "pokračuj", "další krok", "další", "hotovo", "dokončit"
        ]
        
        # Kontrola, zda poslední zpráva obsahuje některou z trigger frází
        for phrase in trigger_phrases:
            if phrase in last_message:
                print(f"Uživatel požádal o vytvoření nabídky: '{phrase}'")
                new_state["current_step"] = Step.GENERATE_PROPOSAL
                new_state["chat_history"] = state.get("chat_history", []) + [
                    {"role": "assistant", "content": "Super, mám dostatek informací k vytvoření nabídky na implementaci produktu MidPoint. Pokračuji v procesu tvorby nabídky."}
                ]
                return new_state
        
        # Vytvoření LLM
        llm = ChatOpenAI(
            model=config.model_name,
            temperature=0.2,
            openai_api_key=config.openai_api_key
        )
        
        # Vytvoření zpráv pro prompt
        system_message = SystemMessage(content="""
        Jsi asistent pro sběr informací pro vytvoření nabídky na implementaci produktu MidPoint.
        Tvým úkolem je zpracovat odpověď uživatele a extrahovat z ní relevantní informace.
        
        Odpověz ve dvou částech:
        1. Potvrzení - potvrď, že jsi pochopil informace od uživatele
        2. Další otázka - pokud stále chybí nějaké informace, zeptej se na ně
        
        Pokud máš všechny potřebné informace nebo jsi již položil několik otázek, informuj uživatele, že může přistoupit k vytvoření nabídky napsáním "vytvoř nabídku" nebo "pokračuj".
        """)
        
        human_message = HumanMessage(content=f"""
        Historie konverzace:
        {json.dumps(chat_history[-5:], ensure_ascii=False, indent=2)}
        
        Poslední zpráva od uživatele:
        {chat_history[-1]["content"]}
        
        Dosud shromážděné informace:
        {json.dumps(state.get("collected_data", {}), ensure_ascii=False, indent=2)}
        
        Počet položených otázek: {step_counter.get(Step.GATHER_INFORMATION, 0)}
        """)
        
        # Generování odpovědi
        response = llm.invoke([system_message, human_message])
        
        # Extrakce informací z odpovědi uživatele
        extract_system_message = SystemMessage(content="""
        Jsi asistent pro extrakci strukturovaných dat z textu.
        Tvým úkolem je extrahovat relevantní informace z odpovědi uživatele a vrátit je ve formátu JSON.
        
        Zaměř se na následující oblasti:
        - rozsah_implementace: Jaké moduly a funkce MidPoint klient požaduje
        - casovy_ramec: Kdy klient očekává dokončení implementace
        - integrace: S jakými systémy má být MidPoint integrován
        - specificke_pozadavky: Jaké má klient specifické požadavky na implementaci
        - rozpocet: Jaký má klient rozpočet na implementaci
        
        Vrať pouze JSON objekt s těmito klíči, pokud jsou informace dostupné. Pokud některá informace chybí, nezahrnuj ji do výstupu.
        """)
        
        extract_human_message = HumanMessage(content=f"""
        Odpověď uživatele:
        {chat_history[-1]["content"]}
        """)
        
        # Generování extrakce
        extract_response = llm.invoke([extract_system_message, extract_human_message])
        
        try:
            # Parsování JSON odpovědi
            extracted_data = json.loads(extract_response.content)
            
            # Aktualizace shromážděných dat
            collected_data = state.get("collected_data", {})
            collected_data.update(extracted_data)
            new_state["collected_data"] = collected_data
        except:
            # Pokud se nepodařilo parsovat JSON, ignorujeme
            pass
        
        # Přidání odpovědi do historie
        response_content = response.content
        
        # Pokud jsme již položili několik otázek, přidáme explicitní výzvu k vytvoření nabídky
        if step_counter.get(Step.GATHER_INFORMATION, 0) >= 3:
            if "vytvoř nabídku" not in response_content.lower() and "pokračuj" not in response_content.lower():
                response_content += "\n\nPokud máte všechny potřebné informace, můžete napsat 'vytvoř nabídku' nebo 'pokračuj' a já vygeneruji nabídku na základě poskytnutých informací."
        
        new_state["chat_history"] = chat_history + [
            {"role": "assistant", "content": response_content}
        ]
    
    return new_state

# Funkce pro generování nabídky
def generate_proposal(state: ProposalState) -> ProposalState:
    """
    Generuje data pro nabídku.
    
    Args:
        state: Aktuální stav
        
    Returns:
        ProposalState: Aktualizovaný stav
    """
    print("Začínám generovat nabídku...")
    
    # Vytvoření LLM
    llm = ChatOpenAI(
        model=config.model_name,
        temperature=0.2,
        openai_api_key=config.openai_api_key
    )
    
    # Získání relevantního kontextu
    context = similarity_search(state["client_request"], k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in context]) if context else "Nebyly nalezeny žádné relevantní dokumenty."
    
    # Vytvoření zpráv pro prompt
    system_message = SystemMessage(content="""
    Jsi asistent pro generování strukturovaných dat pro obchodní nabídky na implementaci produktu MidPoint.
    Na základě poptávky klienta, shromážděných informací a relevantního kontextu vytvoř strukturovaná data pro nabídku.
    
    Výstup musí být ve formátu JSON s následujícími klíči:
    - client_name: Název klienta
    - introduction: Úvod nabídky (1-2 odstavce)
    - solution_description: Popis řešení MidPoint (3-5 odstavců)
    - scope_of_work: Rozsah prací (seznam položek s popisem)
    - timeline: Harmonogram implementace (seznam fází s časovým odhadem)
    - pricing: Cenová kalkulace (tabulka položek s cenami)
    - contact_info: Kontaktní informace
    
    Vrať pouze validní JSON objekt bez dalšího textu nebo vysvětlení.
    """)
    
    human_message = HumanMessage(content=f"""
    Poptávka klienta:
    {state["client_request"]}
    
    Název klienta: {state["client_name"]}
    
    Shromážděné informace:
    {json.dumps(state.get("collected_data", {}), ensure_ascii=False, indent=2)}
    
    Historie konverzace:
    {json.dumps(state.get("chat_history", [])[-10:], ensure_ascii=False, indent=2)}
    
    Relevantní kontext z předchozích nabídek:
    {context_text}
    """)
    
    # Generování dat
    print("Generuji data pro nabídku...")
    response = llm.invoke([system_message, human_message])
    print(f"Odpověď od LLM: {response.content[:500]}...")  # Zobrazíme jen prvních 500 znaků
    
    # Parsování JSON odpovědi
    try:
        # Pokusíme se najít JSON v odpovědi (může být obklopen dalším textem)
        import re
        json_match = re.search(r'({[\s\S]*})', response.content)
        if json_match:
            json_str = json_match.group(1)
            print(f"Nalezen JSON v odpovědi: {json_str[:200]}...")  # Zobrazíme jen prvních 200 znaků
            proposal_data = json.loads(json_str)
        else:
            print("JSON nebyl nalezen v odpovědi, zkouším parsovat celou odpověď")
            proposal_data = json.loads(response.content)
        
        # Kontrola, zda obsahuje všechny požadované klíče
        required_keys = ["client_name", "introduction", "solution_description", "scope_of_work", "timeline", "pricing", "contact_info"]
        missing_keys = [key for key in required_keys if key not in proposal_data]
        
        if missing_keys:
            print(f"Chybí klíče v datech: {missing_keys}")
            # Doplníme chybějící klíče
            for key in missing_keys:
                if key == "client_name":
                    proposal_data[key] = state["client_name"]
                else:
                    proposal_data[key] = f"Chybí informace pro {key}"
    except Exception as e:
        print(f"Chyba při parsování JSON: {e}")
        # Pokud se nepodařilo parsovat JSON, použijeme celou odpověď jako text
        proposal_data = {
            "client_name": state["client_name"],
            "introduction": "Úvod nabídky",
            "solution_description": response.content,
            "scope_of_work": "Rozsah prací",
            "timeline": "Harmonogram implementace",
            "pricing": "Cenová kalkulace",
            "contact_info": "Kontaktní informace"
        }
    
    print(f"Vygenerovaná data pro nabídku: {json.dumps(proposal_data, ensure_ascii=False)[:500]}...")  # Zobrazíme jen prvních 500 znaků
    
    # Aktualizace stavu
    new_state = state.copy()
    new_state["proposal_data"] = proposal_data
    new_state["current_step"] = Step.CREATE_DOCUMENT
    new_state["chat_history"] = state.get("chat_history", []) + [
        {"role": "assistant", "content": "Nabídka byla vygenerována. Nyní vytvářím dokument..."}
    ]
    
    # Aktualizace počítadla kroků
    step_counter = new_state.get("step_counter", {})
    step_counter[Step.GENERATE_PROPOSAL] = step_counter.get(Step.GENERATE_PROPOSAL, 0) + 1
    new_state["step_counter"] = step_counter
    
    print("Generování nabídky dokončeno, přecházím k vytvoření dokumentu")
    return new_state

# Funkce pro vytvoření dokumentu
def create_document(state: ProposalState) -> ProposalState:
    """
    Vytváří dokument nabídky.
    
    Args:
        state: Aktuální stav
        
    Returns:
        ProposalState: Aktualizovaný stav
    """
    print("Začínám vytvářet dokument...")
    
    # Aktualizace počítadla kroků
    new_state = state.copy()
    step_counter = new_state.get("step_counter", {})
    step_counter[Step.CREATE_DOCUMENT] = step_counter.get(Step.CREATE_DOCUMENT, 0) + 1
    new_state["step_counter"] = step_counter
    
    # Kontrola, zda máme data pro nabídku
    if not state.get("proposal_data"):
        print("Chybí data pro nabídku, vracím se ke generování nabídky")
        # Aktualizace stavu
        new_state["current_step"] = Step.GENERATE_PROPOSAL
        new_state["chat_history"] = state.get("chat_history", []) + [
            {"role": "assistant", "content": "Nemám dostatek dat pro vytvoření nabídky. Zkusím je vygenerovat znovu."}
        ]
        return new_state
    
    # Vytvoření dokumentu
    print(f"Vytvářím dokument s daty: {json.dumps(state['proposal_data'], ensure_ascii=False)[:200]}...")  # Zobrazíme jen prvních 200 znaků
    try:
        from app.utils.docx_generator import create_proposal_document
        
        # Kontrola, zda všechny hodnoty v proposal_data jsou řetězce
        proposal_data = state["proposal_data"].copy()
        for key, value in proposal_data.items():
            if not isinstance(value, str):
                proposal_data[key] = str(value)
        
        document_path = create_proposal_document(proposal_data)
        print(f"Dokument byl vytvořen na cestě: {document_path}")
        
        # Kontrola, zda byl dokument skutečně vytvořen
        if document_path == "Chyba při ukládání dokumentu" or not document_path:
            raise Exception("Nepodařilo se vytvořit dokument")
            
        # Kontrola, zda soubor existuje
        if not os.path.exists(document_path):
            print(f"Varování: Soubor {document_path} neexistuje, přestože byl údajně vytvořen")
            
            # Zkusíme vytvořit adresář pro dokument
            os.makedirs(os.path.dirname(document_path), exist_ok=True)
            
            # Zkusíme znovu vytvořit dokument
            document_path = create_proposal_document(proposal_data)
            print(f"Druhý pokus o vytvoření dokumentu: {document_path}")
            
            if not os.path.exists(document_path):
                raise Exception(f"Soubor {document_path} stále neexistuje po druhém pokusu")
        
        # Aktualizace stavu
        new_state["document_path"] = document_path
        new_state["current_step"] = Step.HUMAN_FEEDBACK
        new_state["chat_history"] = state.get("chat_history", []) + [
            {"role": "assistant", "content": f"Dokument byl úspěšně vytvořen a uložen na: {document_path}. Můžete si ho prohlédnout a poskytnout zpětnou vazbu."}
        ]
        
        print(f"Dokument byl úspěšně vytvořen a uložen na: {document_path}")
        return new_state
        
    except Exception as e:
        print(f"Chyba při vytváření dokumentu: {e}")
        # Aktualizace stavu
        new_state["current_step"] = Step.HUMAN_FEEDBACK
        new_state["chat_history"] = state.get("chat_history", []) + [
            {"role": "assistant", "content": f"Při vytváření dokumentu došlo k chybě: {e}. Můžete zkusit vygenerovat nabídku znovu nebo pokračovat bez dokumentu."}
        ]
        return new_state

# Funkce pro rozhodnutí o dalším kroku
def decide_next_step(state: ProposalState) -> str:
    """
    Rozhoduje o dalším kroku na základě aktuálního stavu.
    
    Args:
        state: Aktuální stav
        
    Returns:
        str: Další krok
    """
    current_step = state.get("current_step", Step.ANALYZE_REQUEST)
    step_counter = state.get("step_counter", {})
    
    print(f"Rozhoduji o dalším kroku. Aktuální krok: {current_step}, počítadla: {step_counter}")
    
    # Kontrola počtu opakování - prevence nekonečné rekurze
    for step, count in step_counter.items():
        if count > 20:  # Maximální počet opakování jednoho kroku
            print(f"Překročen maximální počet opakování kroku {step}, přecházím na END")
            return Step.END
    
    # Pokud jsme ve fázi sběru informací a máme poslední zprávu od uživatele
    if current_step == Step.GATHER_INFORMATION:
        chat_history = state.get("chat_history", [])
        
        # Pokud nemáme historii nebo poslední zpráva není od uživatele, zůstáváme ve stejném kroku
        if not chat_history or chat_history[-1]["role"] != "user":
            print("Poslední zpráva není od uživatele, zůstáváme ve fázi sběru informací")
            return Step.GATHER_INFORMATION
        
        # Kontrola, zda uživatel chce přejít k vytvoření nabídky
        last_message = chat_history[-1]["content"].lower().strip()
        print(f"Poslední zpráva od uživatele: '{last_message}'")
        
        # Přímá kontrola na přesnou shodu s příkazem
        if last_message == "vytvoř nabídku":
            print("Přesná shoda s příkazem 'vytvoř nabídku', přecházím na GENERATE_PROPOSAL")
            return Step.GENERATE_PROPOSAL
        
        trigger_phrases = [
            "vytvoř nabídku", "generuj nabídku", "vytvor nabidku", 
            "vygeneruj nabídku", "udělej nabídku", "připrav nabídku",
            "pokračuj", "další krok", "další", "hotovo", "dokončit",
            "ano", "souhlasím", "ok", "dobře", "v pořádku"
        ]
        
        # Přímé porovnání s trigger_phrases
        for phrase in trigger_phrases:
            if phrase in last_message:
                print(f"Nalezena trigger fráze: '{phrase}', přecházím na GENERATE_PROPOSAL")
                return Step.GENERATE_PROPOSAL
        
        # Kontrola jednoduchých příkazů
        simple_commands = ["vytvoř", "generuj", "vytvor", "vygeneruj", "udělej", "připrav"]
        for cmd in simple_commands:
            if cmd in last_message and ("nabídku" in last_message or "nabidku" in last_message):
                print(f"Nalezen příkaz: '{cmd}' + 'nabídku', přecházím na GENERATE_PROPOSAL")
                return Step.GENERATE_PROPOSAL
        
        # Kontrola počtu otázek - po 5 otázkách automaticky přejdeme k vytvoření nabídky
        question_count = step_counter.get(Step.GATHER_INFORMATION, 0)
        if question_count >= 5:
            print(f"Dosažen maximální počet otázek ({question_count}), přecházím na GENERATE_PROPOSAL")
            return Step.GENERATE_PROPOSAL
        
        # Jinak zůstáváme ve fázi sběru informací
        return Step.GATHER_INFORMATION
    
    # Pokud jsme ve fázi generování nabídky, přejdeme k vytvoření dokumentu
    elif current_step == Step.GENERATE_PROPOSAL:
        print("Jsme ve fázi generování nabídky, přecházím k vytvoření dokumentu")
        return Step.CREATE_DOCUMENT
    
    # Pokud jsme ve fázi vytváření dokumentu, přejdeme k interakci s uživatelem
    elif current_step == Step.CREATE_DOCUMENT:
        print("Jsme ve fázi vytváření dokumentu, přecházím k interakci s uživatelem")
        return Step.HUMAN_FEEDBACK
    
    # Pokud jsme ve fázi analýzy poptávky, přejdeme ke sběru informací
    elif current_step == Step.ANALYZE_REQUEST:
        print("Jsme ve fázi analýzy poptávky, přecházím ke sběru informací")
        return Step.GATHER_INFORMATION
    
    # Pokud jsme ve fázi interakce s uživatelem, zůstáváme v ní
    elif current_step == Step.HUMAN_FEEDBACK:
        print("Jsme ve fázi interakce s uživatelem, zůstáváme v ní")
        return Step.HUMAN_FEEDBACK
    
    # Pokud jsme v neznámém stavu, přejdeme k interakci s uživatelem
    else:
        print(f"Neznámý stav: {current_step}, přecházím k interakci s uživatelem")
        return Step.HUMAN_FEEDBACK

# Jednoduchá implementace grafu bez závislosti na LangGraph
class SimpleStateGraph:
    """Jednoduchá implementace grafu stavů bez závislosti na LangGraph."""
    
    def __init__(self):
        self.nodes = {}
        self.entry_point = None
    
    def add_node(self, name, function):
        """Přidá uzel do grafu."""
        self.nodes[name] = function
    
    def set_entry_point(self, name):
        """Nastaví počáteční uzel."""
        self.entry_point = name
    
    def invoke(self, state):
        """Spustí graf s daným stavem."""
        current_step = state.get("current_step", self.entry_point)
        print(f"Aktuální krok: {current_step}")
        
        # Kontrola počtu rekurzivních volání
        recursion_count = state.get("_recursion_count", 0) + 1
        state["_recursion_count"] = recursion_count
        
        # Pokud je krok END, vrátíme stav beze změny
        if current_step == Step.END or current_step == "end":
            print("Dosažen koncový stav, ukončuji.")
            state["current_step"] = "end"
            return state
        
        # Spustíme funkci pro aktuální krok
        if current_step in self.nodes:
            try:
                print(f"Spouštím funkci pro krok: {current_step}")
                
                # Kontrola, zda poslední zpráva od uživatele obsahuje příkaz k vytvoření nabídky
                if current_step == Step.GATHER_INFORMATION:
                    chat_history = state.get("chat_history", [])
                    if chat_history and chat_history[-1]["role"] == "user":
                        last_message = chat_history[-1]["content"].lower().strip()
                        if "vytvoř nabídku" in last_message or "vytvor nabidku" in last_message:
                            print("Detekován příkaz k vytvoření nabídky, přecházím na GENERATE_PROPOSAL")
                            state["current_step"] = Step.GENERATE_PROPOSAL
                            state["chat_history"] = state.get("chat_history", []) + [
                                {"role": "assistant", "content": "Super, mám dostatek informací k vytvoření nabídky na implementaci produktu MidPoint. Pokračuji v procesu tvorby nabídky."}
                            ]
                            # Spustíme funkci pro generování nabídky
                            state = self.nodes[Step.GENERATE_PROPOSAL](state)
                            print(f"Funkce pro krok {Step.GENERATE_PROPOSAL} dokončena.")
                            print(f"Nový stav po generování nabídky: current_step={state['current_step']}")
                            
                            # Pokud se stav změnil na CREATE_DOCUMENT, spustíme funkci pro vytvoření dokumentu
                            if state["current_step"] == Step.CREATE_DOCUMENT:
                                print("Stav změněn na CREATE_DOCUMENT, pokračuji ve vytváření dokumentu")
                                state = self.nodes[Step.CREATE_DOCUMENT](state)
                                print(f"Funkce pro krok {Step.CREATE_DOCUMENT} dokončena.")
                                print(f"Nový stav po vytvoření dokumentu: current_step={state['current_step']}")
                            
                            return state
                
                # Spuštění funkce pro aktuální krok
                state = self.nodes[current_step](state)
                print(f"Funkce pro krok {current_step} dokončena.")
                print(f"Nový stav: current_step={state['current_step']}")
                
                # Kontrola, zda se stav změnil na GENERATE_PROPOSAL
                if state["current_step"] == Step.GENERATE_PROPOSAL and current_step == Step.GATHER_INFORMATION:
                    print("Stav změněn na GENERATE_PROPOSAL, pokračuji v generování nabídky")
                    state = self.nodes[Step.GENERATE_PROPOSAL](state)
                    print(f"Funkce pro krok {Step.GENERATE_PROPOSAL} dokončena.")
                    print(f"Nový stav po generování nabídky: current_step={state['current_step']}")
                    
                    # Pokud se stav změnil na CREATE_DOCUMENT, spustíme funkci pro vytvoření dokumentu
                    if state["current_step"] == Step.CREATE_DOCUMENT:
                        print("Stav změněn na CREATE_DOCUMENT, pokračuji ve vytváření dokumentu")
                        state = self.nodes[Step.CREATE_DOCUMENT](state)
                        print(f"Funkce pro krok {Step.CREATE_DOCUMENT} dokončena.")
                        print(f"Nový stav po vytvoření dokumentu: current_step={state['current_step']}")
                    
                    return state
                
                # Kontrola, zda se stav změnil na CREATE_DOCUMENT
                if state["current_step"] == Step.CREATE_DOCUMENT and current_step == Step.GENERATE_PROPOSAL:
                    print("Stav změněn na CREATE_DOCUMENT, pokračuji ve vytváření dokumentu")
                    state = self.nodes[Step.CREATE_DOCUMENT](state)
                    print(f"Funkce pro krok {Step.CREATE_DOCUMENT} dokončena.")
                    print(f"Nový stav po vytvoření dokumentu: current_step={state['current_step']}")
                    return state
                
            except Exception as e:
                print(f"Chyba při spuštění funkce pro krok {current_step}: {e}")
                import traceback
                traceback.print_exc()
                # V případě chyby přejdeme na další krok
                next_step = decide_next_step(state)
                if next_step == current_step:
                    # Pokud by další krok byl stejný, přejdeme na HUMAN_FEEDBACK, abychom zabránili zacyklení
                    state["current_step"] = Step.HUMAN_FEEDBACK
                    state["chat_history"] = state.get("chat_history", []) + [
                        {"role": "assistant", "content": f"Při zpracování kroku {current_step} došlo k chybě: {e}. Můžete mi poskytnout další informace?"}
                    ]
                    return state
                else:
                    state["current_step"] = next_step
                    return self.invoke(state)
        else:
            print(f"Neznámý krok: {current_step}, přecházím na HUMAN_FEEDBACK")
            state["current_step"] = Step.HUMAN_FEEDBACK
            state["chat_history"] = state.get("chat_history", []) + [
                {"role": "assistant", "content": f"Neznámý krok {current_step}. Můžete mi poskytnout další informace?"}
            ]
            return state
        
        # Rozhodneme o dalším kroku
        next_step = decide_next_step(state)
        print(f"Další krok: {next_step}")
        
        # Pokud je další krok END, vrátíme stav
        if next_step == Step.END or next_step == "end":
            print("Další krok je END, ukončuji.")
            state["current_step"] = "end"
            return state
        
        # Pokud je další krok stejný jako aktuální, vrátíme stav
        if next_step == current_step:
            print(f"Další krok je stejný jako aktuální ({current_step}), vracím stav.")
            return state
        
        # Kontrola počtu rekurzivních volání
        if recursion_count > 10:  # Omezení počtu rekurzivních volání
            print(f"Dosažen maximální počet rekurzivních volání ({recursion_count}), ukončuji.")
            state["current_step"] = Step.HUMAN_FEEDBACK
            state["chat_history"] = state.get("chat_history", []) + [
                {"role": "assistant", "content": "Dosažen maximální počet kroků. Můžete mi poskytnout další informace?"}
            ]
            return state
        
        # Jinak nastavíme další krok a spustíme znovu
        print(f"Přecházím z kroku {current_step} na krok {next_step}")
        state["current_step"] = next_step
        return self.invoke(state)

# Vytvoření grafu
def create_proposal_graph():
    """
    Vytváří graf pro generování nabídek.
    
    Returns:
        SimpleStateGraph: Graf pro generování nabídek
    """
    # Vytvoření grafu
    workflow = SimpleStateGraph()
    
    # Definice uzlů
    workflow.add_node(Step.ANALYZE_REQUEST, analyze_request)
    workflow.add_node(Step.GATHER_INFORMATION, gather_information)
    workflow.add_node(Step.GENERATE_PROPOSAL, generate_proposal)
    workflow.add_node(Step.CREATE_DOCUMENT, create_document)
    workflow.add_node(Step.HUMAN_FEEDBACK, lambda x: x)  # Pouze předání stavu
    
    # Nastavení počátečního uzlu
    workflow.set_entry_point(Step.ANALYZE_REQUEST)
    
    return workflow

# Funkce pro inicializaci stavu
def init_proposal_state(client_request: str, client_name: str) -> ProposalState:
    """
    Inicializuje stav pro generování nabídky.
    
    Args:
        client_request: Poptávka klienta
        client_name: Název klienta
        
    Returns:
        ProposalState: Inicializovaný stav
    """
    return {
        "client_request": client_request,
        "client_name": client_name,
        "current_step": Step.ANALYZE_REQUEST,
        "chat_history": [],
        "collected_data": {},
        "proposal_data": None,
        "document_path": None,
        "step_counter": {}  # Počítadlo kroků pro prevenci nekonečné rekurze
    }

# Funkce pro zpracování vstupu uživatele
def process_user_input(state: ProposalState, user_input: str) -> ProposalState:
    """
    Zpracovává vstup uživatele.
    
    Args:
        state: Aktuální stav
        user_input: Vstup uživatele
        
    Returns:
        ProposalState: Aktualizovaný stav
    """
    # Aktualizace stavu
    new_state = state.copy()
    new_state["chat_history"] = state.get("chat_history", []) + [
        {"role": "user", "content": user_input}
    ]
    
    return new_state 