# BidMaster - AI Proposal Generator

BidMaster je nástroj pro automatické generování obchodních nabídek pro implementaci produktu MidPoint. Využívá technologii RAG (Retrieval Augmented Generation) a LLM modely pro vytváření personalizovaných nabídek na základě existujících šablon a klientských požadavků.

## Funkce

- Nahrání a analýza klientské poptávky
- Interaktivní chatbot pro doplnění detailů nabídky
- Vyhledávání relevantních částí z existujících nabídek pomocí vektorové databáze Pinecone
- Generování finálního dokumentu ve formátu DOCX

## Instalace

1. Naklonujte tento repozitář:
```bash
git clone https://github.com/yourusername/BidMaster.git
cd BidMaster
```

2. Vytvořte a aktivujte virtuální prostředí:
```bash
python3 -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate
```

3. Nainstalujte závislosti:
```bash
# Možnost 1: Pomocí pip
pip3 install -r requirements.txt

# Možnost 2: Pomocí instalačního skriptu
python3 install_dependencies.py
```

4. Spusťte skript pro nastavení projektu:
```bash
python3 setup.py
```

5. Upravte soubor `.env` a nastavte správné hodnoty API klíčů:
```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=bidmaster
EMBEDDING_MODEL=text-embedding-3-large
PINECONE_DIMENSION=3072
PINECONE_NAMESPACE=proposals
```

## Řešení problémů

Pokud narazíte na chybu `ModuleNotFoundError: No module named 'langchain_community'` nebo podobnou, ujistěte se, že máte nainstalovány všechny závislosti:

```bash
python3 install_dependencies.py
```

Některé balíčky LangChain prošly restrukturalizací, proto skript obsahuje alternativní importy pro zajištění kompatibility s různými verzemi.

### Problémy s vektorovou databází

Pokud se dokumenty neimportují správně do vektorové databáze nebo je databáze prázdná, zkuste následující:

1. Ujistěte se, že máte správně nastavené proměnné prostředí v souboru `.env`:
```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=bidmaster
EMBEDDING_MODEL=text-embedding-3-large
PINECONE_DIMENSION=3072
PINECONE_NAMESPACE=proposals
```

2. Zkontrolujte, zda existuje index v Pinecone s odpovídající dimenzí:
```bash
python3 manage_proposals.py info
```

3. Pokud index neexistuje nebo má nesprávnou dimenzi, smažte ho a nechte ho vytvořit znovu:
```bash
python3 manage_proposals.py delete
```

4. Importujte nabídky znovu:
```bash
python3 manage_proposals.py import data/proposals
```

5. Ověřte, že import proběhl úspěšně vyhledáním v databázi:
```bash
python3 manage_proposals.py search "implementace" --limit 3
```

## Jak to funguje

BidMaster využívá několik klíčových technologií a postupů pro generování obchodních nabídek:

### 1. Vektorová databáze a RAG (Retrieval Augmented Generation)

BidMaster používá vektorovou databázi Pinecone pro ukládání a vyhledávání relevantních částí existujících nabídek. Proces funguje následovně:

1. **Import dokumentů**:
   - Dokumenty (PDF, DOCX, JSON) jsou načteny ze složky `data/proposals/`
   - Text je extrahován z dokumentů a rozdělen na menší části (chunky) o velikosti 500 znaků s překryvem 100 znaků
   - Každý chunk je převeden na vektor pomocí embeddings modelu (text-embedding-3-large)
   - Vektory jsou uloženy v Pinecone databázi s metadaty obsahujícími informace o původním dokumentu

2. **Vyhledávání**:
   - Při generování nabídky je klientská poptávka převedena na vektor
   - V Pinecone databázi jsou vyhledány nejpodobnější chunky existujících nabídek
   - Tyto chunky jsou použity jako kontext pro LLM model při generování nové nabídky

### 2. LangGraph a stavový automat

Pro interaktivní generování nabídek BidMaster používá LangGraph, což je nadstavba nad LangChain, která umožňuje vytvářet stavové automaty pro komplexní konverzační toky:

1. **Stavový automat**:
   - Aplikace začíná ve stavu `start`, kde se inicializuje konverzace
   - Přechází do stavu `gather_information`, kde sbírá informace od uživatele
   - Když má dostatek informací, přechází do stavu `generate_proposal`, kde generuje nabídku
   - Nakonec přechází do stavu `human_feedback`, kde uživatel může poskytnout zpětnou vazbu

2. **Rozhodovací logika**:
   - Funkce `decide_next_step` rozhoduje, jaký bude další krok v konverzaci
   - Rozhodnutí je založeno na aktuálním stavu konverzace a uživatelském vstupu
   - Systém dokáže detekovat, kdy má dostatek informací pro generování nabídky

### 3. Chunking a správa metadat

Pro efektivní práci s dokumenty BidMaster používá techniku "chunking":

1. **Rozdělení textu na chunky**:
   - Dlouhé dokumenty jsou rozděleny na menší části (chunky)
   - Každý chunk má optimální velikost pro zpracování LLM modelem
   - Chunky se překrývají, aby se zachoval kontext mezi nimi

2. **Metadata**:
   - Každý chunk obsahuje metadata s informacemi o původním dokumentu
   - Metadata zahrnují zdroj, název, jméno klienta, datum, verzi a pozici chunku v dokumentu
   - Velikost metadat je omezena, aby nepřekročila limity Pinecone (40 KB)

### 4. Generování dokumentů

Finální krok je generování dokumentu ve formátu DOCX:

1. **Šablony**:
   - Systém používá šablony ze složky `data/templates/`
   - Šablony obsahují zástupné symboly, které jsou nahrazeny generovaným obsahem

2. **Generování obsahu**:q
   - LLM model generuje obsah na základě klientské poptávky a nalezených relevantních částí
   - Obsah je strukturován podle požadavků na obchodní nabídku

3. **Vytvoření dokumentu**:
   - Vygenerovaný obsah je vložen do šablony
   - Výsledný dokument je uložen do složky `data/generated/`

## Použití

### Příprava databáze nabídek

1. Umístěte existující nabídky do složky `data/proposals/`
2. Spusťte skript pro indexaci nabídek:
```bash
python3 scripts/index_proposals.py
```

Pro resetování vektorové databáze použijte přepínač `-r`:
```bash
python3 scripts/index_proposals.py -r
```

### Spuštění CLI aplikace

```bash
python3 run_cli.py
```

Můžete také specifikovat cestu k souboru s poptávkou a název klienta:
```bash
python3 run_cli.py --client-request data/examples/poptavka_vzor.txt --client-name "Finanční služby, a.s."
```

### Použití interaktivního průvodce

Pro snadnější správu nabídek a poptávek můžete použít interaktivního průvodce:

```bash
python3 bidmaster_cli.py
```

Interaktivní průvodce nabízí následující možnosti:

1. **Import nových nabídek** - Import nabídek ze složky do vektorové databáze
2. **Vyhledávání nabídek** - Vyhledávání v existujících nabídkách podle klíčových slov
3. **Zpracování poptávky** - Spuštění chatbota pro zpracování klientské poptávky
4. **Správa databáze** - Zobrazení informací o databázi nebo její vymazání
5. **Konec** - Ukončení aplikace

Pro spuštění průvodce bez čištění obrazovky použijte přepínač `--no-clear`:
```bash
python3 bidmaster_cli.py --no-clear
```

### Interakce s chatbotem

Po spuštění CLI aplikace budete moci interagovat s chatbotem, který vás provede procesem vytvoření nabídky:

1. Chatbot analyzuje poptávku klienta a identifikuje chybějící informace
2. Chatbot vám bude klást doplňující otázky pro získání potřebných informací
3. Když budete mít všechny potřebné informace, můžete požádat o vygenerování nabídky příkazem "vytvoř nabídku"
4. Chatbot vygeneruje nabídku a vytvoří DOCX dokument
5. Můžete poskytnout zpětnou vazbu a požádat o úpravy nabídky

## Struktura projektu

```
BidMaster/
├── app/                    # Hlavní aplikační kód
│   ├── cli.py              # CLI aplikace
│   ├── components/         # Komponenty UI
│   ├── chains/             # LangChain a LangGraph komponenty
│   │   ├── proposal_chain.py  # LangChain řetězec pro generování nabídek
│   │   └── proposal_graph.py  # LangGraph komponenta pro interaktivní generování nabídek
│   └── utils/              # Pomocné funkce
│       ├── config.py       # Konfigurace aplikace
│       ├── document_processor.py  # Zpracování dokumentů
│       ├── docx_generator.py  # Generování DOCX dokumentů
│       ├── import_proposals.py  # Import nabídek do vektorové databáze
│       └── vector_store.py  # Práce s vektorovou databází
├── data/                   # Data
│   ├── proposals/          # Existující nabídky
│   ├── templates/          # Šablony dokumentů
│   ├── generated/          # Vygenerované dokumenty
│   └── examples/           # Vzorové soubory
├── scripts/                # Skripty pro správu dat
│   ├── index_proposals.py  # Skript pro indexaci nabídek
│   └── create_template.py  # Skript pro vytvoření šablony
├── .env                    # Konfigurační proměnné
├── .env.example            # Vzorový konfigurační soubor
├── bidmaster_cli.py        # Interaktivní průvodce pro správu nabídek
├── manage_proposals.py     # Skript pro správu nabídek v databázi
├── requirements.txt        # Závislosti
├── install_dependencies.py # Skript pro instalaci závislostí
├── run_cli.py              # Hlavní skript pro spuštění CLI aplikace
├── setup.py                # Skript pro nastavení projektu
└── README.md               # Dokumentace
```

## Rozšíření projektu

### Přidání webového rozhraní

Pro vytvoření webového rozhraní můžete implementovat Streamlit aplikaci v souboru `app/main.py`. Poté můžete spustit webovou aplikaci příkazem:

```bash
python3 -m streamlit run app/main.py
```

### Přidání API

Pro vytvoření API můžete implementovat FastAPI backend v souboru `app/api.py`. Poté můžete spustit API příkazem:

```bash
python3 -m uvicorn app.api:app --reload
```

## Licence

Tento projekt je licencován pod MIT licencí - viz soubor LICENSE pro detaily. 