# Changelog

## [1.2.0] - 2023-07-16

### Změněno
- Vyčištění projektu od testovacích skriptů a nepotřebných souborů
- Aktualizace souboru .gitignore pro lepší ignorování systémových a cache souborů

### Odstraněno
- Testovací skripty: test_import.py, test_pdf_import.py, test_document_creation.py, test_state_transition.py, test_proposal_generation.py
- Pomocné skripty pro testování: create_test_pdf.py, convert_text_to_pdf.py, convert_docx_to_pdf.py
- Původní implementace pdfintelisearch.py

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