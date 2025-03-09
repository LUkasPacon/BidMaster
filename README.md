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
PINECONE_ENVIRONMENT=your_pinecone_environment
```

## Řešení problémů

Pokud narazíte na chybu `ModuleNotFoundError: No module named 'langchain_community'` nebo podobnou, ujistěte se, že máte nainstalovány všechny závislosti:

```bash
python3 install_dependencies.py
```

Některé balíčky LangChain prošly restrukturalizací, proto skript obsahuje alternativní importy pro zajištění kompatibility s různými verzemi.

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