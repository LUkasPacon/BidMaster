# Úprava orchestrace pro projekt BidMaster

## Popis provedených úprav

### Pochopení a implementace architektury orchestrace

V rámci projektu BidMaster jsem implementoval vlastní orchestrační systém založený na stavovém automatu, který řídí celý proces generování obchodních nabídek. Místo úpravy existujícího Interest Bota jsem vytvořil specializovaný systém pro generování obchodních nabídek pro implementaci produktu MidPoint.

Klíčovou komponentou je třída `SimpleStateGraph` v souboru `proposal_graph.py`, která implementuje stavový automat s následujícími vlastnostmi:

```python
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
        # Implementace řízení toku zpracování
```

Tato třída umožňuje definovat jednotlivé uzly (stavy) grafu a přechody mezi nimi, což poskytuje flexibilní a rozšiřitelnou architekturu pro orchestraci celého procesu.

### Specifikace cílového projektu

BidMaster je specializovaný nástroj pro automatické generování obchodních nabídek pro implementaci produktu MidPoint. Využívá technologii RAG (Retrieval Augmented Generation) a LLM modely pro vytváření personalizovaných nabídek na základě existujících šablon a klientských požadavků.

Klíčové požadavky a očekávané výstupy:
- Analýza klientské poptávky a identifikace chybějících informací
- Interaktivní sběr doplňujících informací od uživatele
- Vyhledávání relevantních částí z existujících nabídek
- Generování strukturované nabídky
- Vytvoření finálního dokumentu ve formátu DOCX

### Přizpůsobení systému

#### Úprava vstupních dat

Implementoval jsem robustní systém pro zpracování různých typů dokumentů:

1. **Import a zpracování dokumentů**:
   - Podpora pro PDF, DOCX a JSON soubory
   - Extrakce textu a metadat z dokumentů
   - Rozdělení textu na menší části (chunky) pro efektivnější vektorizaci
   - Ukládání do vektorové databáze Pinecone

2. **Optimalizace vektorizace**:
   ```python
   # Vytvoření text splitteru pro rozdělení textu na menší části
   text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=500,
       chunk_overlap=100,
       length_function=len
   )
   
   # Rozdělení textu na chunky
   chunks = text_splitter.split_text(text)
   ```

3. **Správa metadat**:
   - Omezení velikosti metadat na 30 KB (pod limit Pinecone 40 KB)
   - Strukturování metadat pro lepší vyhledávání
   - Přidání informací o pozici chunku v dokumentu

#### Změna promptování

Implementoval jsem sofistikované promptování pro různé fáze procesu:

1. **Analýza poptávky**:
   ```python
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
   ```

2. **Sběr informací**:
   - Implementace doplňujících otázek na základě chybějících informací
   - Adaptivní promptování podle předchozích odpovědí uživatele
   - Detekce, kdy má systém dostatek informací pro generování nabídky

3. **Generování nabídky**:
   - Strukturované promptování pro vytvoření jednotlivých částí nabídky
   - Využití relevantních částí z existujících nabídek jako kontextu
   - Personalizace obsahu podle specifických požadavků klienta

#### Zlepšení rozhodování a výstupu

1. **Relevance scoring a vyhledávání**:
   ```python
   # Získání relevantního kontextu
   context = similarity_search(state["client_request"], k=3)
   context_text = "\n\n---\n\n".join([doc.page_content for doc in context]) if context else "Nebyly nalezeny žádné relevantní dokumenty."
   ```

2. **Rozhodovací logika**:
   ```python
   def decide_next_step(state: ProposalState) -> str:
       """
       Rozhodne, jaký bude další krok v konverzaci.
       
       Args:
           state: Aktuální stav
           
       Returns:
           str: Název dalšího kroku
       """
       # Implementace rozhodovací logiky pro přechody mezi stavy
   ```

3. **Strukturovaný výstup**:
   - Generování DOCX dokumentu s nabídkou
   - Strukturování obsahu podle standardního formátu obchodních nabídek
   - Přidání metadat a formátování pro profesionální vzhled

### Testování a ladění

1. **Optimalizace vektorizace**:
   - Zmenšení velikosti chunků z 1000 na 500 znaků pro lepší přesnost vyhledávání
   - Optimalizace překryvu chunků (100 znaků) pro zachování kontextu
   - Implementace limitů velikosti metadat pro prevenci chyb v Pinecone

2. **Řešení problémů s namespace**:
   ```python
   # Pokud není zadán namespace, použijeme výchozí z konfigurace
   if namespace is None:
       namespace = os.getenv("PINECONE_NAMESPACE", "proposals")
       print(f"Používám výchozí namespace: {namespace}")
   ```

3. **Robustní zpracování chyb**:
   ```python
   try:
       # Spuštění funkce pro aktuální krok
       state = self.nodes[current_step](state)
   except Exception as e:
       print(f"Chyba při spuštění funkce pro krok {current_step}: {e}")
       import traceback
       traceback.print_exc()
       # V případě chyby přejdeme na další krok
   ```

4. **Prevence zacyklení**:
   - Implementace počítadla kroků pro prevenci nekonečné rekurze
   - Automatický přechod do stavu interakce s uživatelem při detekci potenciálního zacyklení

## Ukázka vylepšených odpovědí

### Před úpravou
Původní systém neexistoval nebo byl velmi omezený. Neměl schopnost analyzovat poptávky, interaktivně sbírat informace a generovat strukturované nabídky.

### Po úpravě

#### Analýza poptávky
```
Shrnutí poptávky:
- Klient hledá řešení pro správu identit a přístupů (IAM)
- Potřebuje implementaci MidPoint pro 500 uživatelů
- Požaduje integraci s Active Directory a HR systémem
- Zmiňuje potřebu self-service portálu pro uživatele

Chybějící informace:
1. Časový rámec - kdy klient očekává dokončení implementace?
2. Jaké konkrétní moduly MidPoint klient požaduje?
3. Jaké jsou specifické požadavky na workflow schvalování?
4. Jaký je rozpočet projektu?
5. Jaké jsou požadavky na školení a podporu po implementaci?
```

#### Interaktivní sběr informací
```
Děkuji za informaci o časovém rámci. Implementace do 3 měsíců je realistický cíl.

Nyní bych potřeboval vědět více o požadovaných modulech MidPoint. Zajímá vás:
1. Role management (správa rolí a oprávnění)
2. Workflow management (schvalovací procesy)
3. Self-service (portál pro uživatele)
4. Reporting a audit
5. Rekonciliace (synchronizace dat mezi systémy)

Které z těchto modulů jsou pro vás prioritou?
```

#### Generování nabídky
```
Na základě našeho rozhovoru jsem připravil nabídku implementace MidPoint pro vaši společnost. Nabídka zahrnuje:

1. Implementaci MidPoint s moduly:
   - Role management
   - Workflow management
   - Self-service portál
   - Reporting a audit

2. Integrace s:
   - Active Directory
   - HR systémem SAP

3. Časový harmonogram:
   - Analýza a návrh: 3 týdny
   - Implementace: 6 týdnů
   - Testování: 2 týdny
   - Školení a nasazení: 1 týden

4. Cenová kalkulace:
   - Licence: 15 000 EUR
   - Implementace: 25 000 EUR
   - Školení: 5 000 EUR
   - Podpora (1 rok): 10 000 EUR

Dokument s nabídkou byl vytvořen a uložen do: data/generated/nabidka_implementace_midpoint_2023-07-16.docx
```

## Kód úprav

### Implementace stavového automatu
```python
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
        
        # Implementace řízení toku zpracování
```

### Definice stavů
```python
class Step(str, Enum):
    """Kroky v procesu generování nabídky."""
    
    ANALYZE_REQUEST = "analyze_request"
    GATHER_INFORMATION = "gather_information"
    GENERATE_PROPOSAL = "generate_proposal"
    CREATE_DOCUMENT = "create_document"
    HUMAN_FEEDBACK = "human_feedback"
    END = "end"  # Explicitní konec
```

### Rozhodovací logika
```python
def decide_next_step(state: ProposalState) -> str:
    """
    Rozhodne, jaký bude další krok v konverzaci.
    
    Args:
        state: Aktuální stav
        
    Returns:
        str: Název dalšího kroku
    """
    current_step = state.get("current_step", Step.ANALYZE_REQUEST)
    chat_history = state.get("chat_history", [])
    step_counter = state.get("step_counter", {})
    
    # Implementace rozhodovací logiky pro přechody mezi stavy
```

## Závěr

Projekt BidMaster představuje komplexní řešení pro automatické generování obchodních nabídek s využitím moderních technologií jako RAG a LLM. Implementovaná orchestrace pomocí stavového automatu zajišťuje plynulý a řízený průběh celého procesu od analýzy poptávky až po vytvoření finálního dokumentu s nabídkou.

Klíčové přínosy implementované orchestrace:
1. Flexibilní a rozšiřitelná architektura
2. Robustní zpracování chyb a prevence zacyklení
3. Adaptivní interakce s uživatelem
4. Efektivní vyhledávání relevantních informací
5. Strukturované generování výstupů

Tento projekt demonstruje pokročilé možnosti orchestrace AI systémů a jejich praktické využití v reálných business procesech. 