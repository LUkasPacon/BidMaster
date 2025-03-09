# Správa nabídek v BidMaster

Tento dokument popisuje, jak spravovat nabídky v systému BidMaster, včetně importu nových nabídek do vektorové databáze, vyhledávání a mazání.

## Přehled

BidMaster používá vektorovou databázi Pinecone pro ukládání a vyhledávání relevantních informací při generování nabídek. Nabídky jsou uloženy jako vektory, které reprezentují sémantický obsah dokumentů. Při generování nové nabídky systém vyhledá podobné nabídky, které mohou sloužit jako inspirace.

## Požadavky

Pro správu nabídek potřebujete:

1. Nainstalované závislosti BidMaster
2. Přístup k Pinecone (API klíč a správně nakonfigurovaný index)
3. Nabídky ve formátu DOCX, PDF nebo JSON

## Formáty nabídek

BidMaster podporuje tři formáty nabídek:

### PDF formát

Standardní PDF dokumenty s nabídkami. Systém extrahuje text a metadata z dokumentu. Podporovány jsou textové PDF soubory, ze kterých lze extrahovat text. PDF soubory, které obsahují pouze naskenované obrázky, nemusí být správně zpracovány.

### DOCX formát

Standardní dokumenty Microsoft Word s nabídkami. Systém extrahuje text a metadata z dokumentu.

### JSON formát

Strukturovaná data ve formátu JSON s následujícími klíči:

```json
{
  "client_name": "Název klienta",
  "introduction": "Úvod nabídky",
  "solution_description": "Popis řešení",
  "scope_of_work": "Rozsah prací",
  "timeline": "Harmonogram",
  "pricing": "Cenová kalkulace",
  "contact_info": "Kontaktní informace"
}
```

## Správa nabídek pomocí CLI

BidMaster obsahuje skript `manage_proposals.py` pro správu nabídek z příkazové řádky.

### Import nabídek

Pro import nabídek do vektorové databáze použijte příkaz:

```bash
python manage_proposals.py import <cesta_k_adresáři>
```

Příklad:

```bash
python manage_proposals.py import data/examples/proposals
```

Volitelné parametry:
- `--namespace`: Namespace pro vektorovou databázi (volitelné)

### Vyhledávání nabídek

Pro vyhledávání podobných nabídek použijte příkaz:

```bash
python manage_proposals.py search "<dotaz>"
```

Příklad:

```bash
python manage_proposals.py search "implementace MidPoint pro bankovní sektor"
```

Volitelné parametry:
- `--limit`: Maximální počet výsledků (výchozí: 5)

### Mazání nabídek

Pro smazání všech nabídek z vektorové databáze použijte příkaz:

```bash
python manage_proposals.py delete
```

**Upozornění**: Tento příkaz smaže všechny vektory z databáze. Používejte ho opatrně!

### Zobrazení informací

Pro zobrazení informací o konfiguraci použijte příkaz:

```bash
python manage_proposals.py info
```

## Struktura adresářů pro nabídky

Doporučená struktura adresářů pro nabídky:

```
data/
  proposals/
    pdf/
      nabidka1.pdf
      nabidka2.pdf
      ...
    docx/
      nabidka1.docx
      nabidka2.docx
      ...
    json/
      nabidka1.json
      nabidka2.json
      ...
```

## Tipy pro efektivní správu nabídek

1. **Organizace nabídek**: Udržujte nabídky organizované podle typu, klienta nebo data.
2. **Kvalita dat**: Ujistěte se, že nabídky obsahují relevantní a kvalitní informace.
3. **Pravidelné aktualizace**: Pravidelně aktualizujte databázi novými nabídkami.
4. **Zálohování**: Před mazáním databáze si vytvořte zálohu nabídek.
5. **Testování**: Po importu nabídek otestujte vyhledávání, abyste ověřili, že nabídky jsou správně indexovány.

## Řešení problémů

### Problém: Import nabídek selže

Možné příčiny:
- Nesprávný formát nabídek
- Problémy s připojením k Pinecone
- Nesprávná konfigurace API klíčů

Řešení:
1. Zkontrolujte formát nabídek
2. Ověřte připojení k Pinecone
3. Zkontrolujte konfiguraci v souboru `.env`

### Problém: Vyhledávání nevrací očekávané výsledky

Možné příčiny:
- Nedostatek relevantních nabídek v databázi
- Nesprávně formulovaný dotaz
- Problémy s vektorovou reprezentací

Řešení:
1. Importujte více relevantních nabídek
2. Upravte dotaz, aby lépe vystihoval hledaný obsah
3. Zkontrolujte konfiguraci embedding modelu 