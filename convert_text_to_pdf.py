#!/usr/bin/env python3
"""
Skript pro konverzi textového souboru na PDF.
"""
import sys
import os
from pathlib import Path
import argparse

def convert_text_to_pdf(text_path, pdf_path=None):
    """
    Konvertuje textový soubor na PDF.
    
    Args:
        text_path: Cesta k textovému souboru
        pdf_path: Cesta k výstupnímu PDF souboru (volitelné)
    
    Returns:
        str: Cesta k vytvořenému PDF souboru
    """
    try:
        # Pokud není zadána cesta k výstupnímu souboru, vytvoříme ji
        if pdf_path is None:
            pdf_path = os.path.splitext(text_path)[0] + ".pdf"
        
        # Kontrola, zda vstupní soubor existuje
        if not os.path.exists(text_path):
            print(f"Soubor {text_path} neexistuje!")
            return None
        
        # Pokus o import knihovny pro konverzi
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # Načtení textu ze souboru
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Vytvoření PDF
            c = canvas.Canvas(pdf_path, pagesize=A4)
            
            # Registrace fontu s podporou českých znaků
            try:
                # Pokus o registraci DejaVuSans
                pdfmetrics.registerFont(TTFont('DejaVuSans', '/Library/Fonts/DejaVuSans.ttf'))
                font_name = 'DejaVuSans'
            except:
                try:
                    # Pokus o registraci Arial
                    pdfmetrics.registerFont(TTFont('Arial', '/Library/Fonts/Arial.ttf'))
                    font_name = 'Arial'
                except:
                    # Použití výchozího fontu
                    font_name = 'Helvetica'
            
            # Nastavení fontu
            c.setFont(font_name, 12)
            
            # Rozdělení textu na řádky
            lines = text.split('\n')
            
            # Nastavení pozice
            y = 800
            line_height = 14
            
            # Přidání řádků do PDF
            for line in lines:
                # Kontrola, zda řádek začíná nadpisem (velkými písmeny)
                if line.strip() and line.strip().isupper():
                    c.setFont(font_name + '-Bold' if font_name != 'Helvetica' else 'Helvetica-Bold', 14)
                    c.drawString(50, y, line)
                    y -= line_height + 2
                    c.setFont(font_name, 12)
                else:
                    c.drawString(50, y, line)
                    y -= line_height
                
                # Pokud jsme na konci stránky, přidáme novou
                if y < 50:
                    c.showPage()
                    y = 800
                    c.setFont(font_name, 12)
            
            # Uložení PDF
            c.save()
            
            # Kontrola, zda byl PDF soubor vytvořen
            if os.path.exists(pdf_path):
                print(f"Konverze dokončena. PDF soubor byl vytvořen: {pdf_path}")
                return pdf_path
            else:
                print(f"Konverze selhala. PDF soubor nebyl vytvořen.")
                return None
        except ImportError:
            print("Knihovna reportlab není nainstalována. Použijte 'pip3 install reportlab'.")
            return None
    except Exception as e:
        print(f"Chyba při konverzi: {e}")
        return None

def main():
    """
    Hlavní funkce pro spuštění konverze.
    """
    parser = argparse.ArgumentParser(description="Konverze textového souboru na PDF")
    parser.add_argument("text_path", help="Cesta k textovému souboru")
    parser.add_argument("--pdf_path", help="Cesta k výstupnímu PDF souboru (volitelné)")
    
    args = parser.parse_args()
    
    convert_text_to_pdf(args.text_path, args.pdf_path)

if __name__ == "__main__":
    main() 