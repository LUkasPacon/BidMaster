#!/usr/bin/env python3
"""
Skript pro vytvoření testovacího PDF souboru.
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_test_pdf(output_path="data/proposals/pdf/test_proposal.pdf"):
    """
    Vytvoří testovací PDF soubor.
    
    Args:
        output_path: Cesta k výstupnímu PDF souboru
    """
    # Vytvoření adresáře, pokud neexistuje
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Vytvoření PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # Nastavení fontu
    font_name = 'Helvetica'
    
    # Nastavení fontu
    c.setFont(font_name, 12)
    
    # Přidání obsahu
    y = 800
    
    # Nadpis
    c.setFont('Helvetica-Bold', 16)
    c.drawString(50, y, "NABÍDKA IMPLEMENTACE MIDPOINT")
    y -= 30
    
    # Klient
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, "pro XYZ Corporation, a.s.")
    y -= 30
    
    # Datum a verze
    c.setFont('Helvetica', 12)
    c.drawString(50, y, "ze dne 10.3.2025")
    y -= 20
    c.drawString(50, y, "verze: 1.0")
    y -= 40
    
    # Úvod
    c.drawString(50, y, "Vážený pane Nováku,")
    y -= 20
    
    text = "děkujeme za Váš zájem o implementaci řešení MidPoint pro správu identit a přístupů (IAM)"
    c.drawString(50, y, text)
    y -= 20
    
    text = "ve Vaší společnosti. Na základě Vaší poptávky Vám předkládáme nabídku implementace MidPoint,"
    c.drawString(50, y, text)
    y -= 20
    
    text = "která pokrývá všechny Vámi požadované funkcionality a integrační scénáře."
    c.drawString(50, y, text)
    y -= 40
    
    # Popis řešení
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, "POPIS ŘEŠENÍ")
    y -= 30
    
    c.setFont('Helvetica', 12)
    text = "MidPoint je open-source řešení pro správu identit a přístupů, které poskytuje komplexní"
    c.drawString(50, y, text)
    y -= 20
    
    text = "funkcionalitu pro centralizovanou správu uživatelských účtů, automatizaci procesů zřizování"
    c.drawString(50, y, text)
    y -= 20
    
    text = "a rušení přístupů, řízení životního cyklu identit a reporting."
    c.drawString(50, y, text)
    y -= 40
    
    # Uložení PDF
    c.save()
    
    print(f"Testovací PDF soubor byl vytvořen: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_pdf() 