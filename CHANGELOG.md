# Changelog

## [1.1.0] - 2023-07-15

### Přidáno
- Interaktivní průvodce pro správu nabídek (`bidmaster_cli.py`)
- Skript pro správu nabídek v databázi (`manage_proposals.py`)
- Podrobná dokumentace o fungování systému v README.md

### Změněno
- Vylepšený import nabídek do vektorové databáze s podporou chunkingu
- Optimalizace velikosti metadat pro Pinecone (omezení na 30 KB)
- Rozdělení textu na menší části (chunky) o velikosti 500 znaků s překryvem 100 znaků
- Lepší zpracování chyb při importu a vyhledávání

### Opraveno
- Problém s prázdnou vektorovou databází
- Problém s nekonzistentním použitím namespace
- Problém s velikostí metadat překračující limity Pinecone
- Problém s importem třídy Document z langchain_core.documents

## [1.0.0] - 2023-06-30

### Přidáno
- Základní funkcionalita pro generování obchodních nabídek
- Podpora pro import PDF, DOCX a JSON souborů
- Vektorová databáze Pinecone pro ukládání a vyhledávání nabídek
- LangGraph komponenta pro interaktivní generování nabídek
- CLI aplikace pro zpracování klientských poptávek 