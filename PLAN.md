# MDitD - MarkItDown Web Aplikácia

## Popis projektu
Rýchla web aplikácia na konverziu rôznych dokumentov do Markdown formátu pomocou Microsoft MarkItDown knižnice.

## Cieľ
Vytvoriť jednoduchú web aplikáciu s upload formulárom, ktorá:
- Príjme dokumenty cez web interface
- Konvertuje ich do MD súborov pomocou MarkItDown
- Uloží výsledky do vybraného adresára (default: `vystup/`)

## Technický stack
- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Bootstrap CSS
- **Conversion**: Microsoft MarkItDown
- **File handling**: python-multipart

## Podporované formáty
- Office dokumenty: Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
- PDF súbory (s OCR podporou)
- Obrázky (s EXIF metadata a OCR)
- Audio súbory (s transkripciou)
- Web/štruktúrované dáta: HTML, CSV, JSON, XML
- Archívy: ZIP súbory

## Štruktúra projektu
```
MDitD/
├── main.py              # FastAPI aplikácia, hlavný entry point
├── utils/
│   ├── __init__.py      # Package inicializácia
│   ├── converter.py     # MarkItDown konverzia logika
│   └── file_handler.py  # File management operácie
├── templates/           # Jinja2 HTML šablóny
│   ├── index.html       # Hlavná stránka s upload formom
│   ├── success.html     # Úspešná konverzia stránka
│   └── error.html       # Error handling stránka
├── static/              # Statické súbory
│   ├── css/
│   │   └── style.css    # Vlastné CSS štýly
│   └── js/
│       └── app.js       # Frontend JavaScript
├── vystup/              # Default výstupný adresár pre MD súbory
├── uploads/             # Dočasný adresár pre nahraté súbory
├── pyproject.toml       # Python projekt konfigurácia
└── README.md            # Dokumentácia projektu
```

## Funkcionality
1. **Upload Interface**: Web formulár na nahrávanie súborov
2. **Directory Selection**: Možnosť výberu cieľového adresára
3. **Batch Processing**: Podpora pre viacero súborov naraz
4. **Progress Feedback**: Indikátor postupu konverzie
5. **Error Handling**: Správne spracovanie chýb a nepodporovaných formátov
6. **File Preview**: Náhľad konvertovaného Markdown obsahu