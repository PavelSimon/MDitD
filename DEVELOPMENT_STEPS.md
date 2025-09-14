# Vývojové kroky - MDitD

## Fáza 1: Príprava projektu
### Krok 1.1: Konfigurácia závislostí ✅
- **Súbor**: `pyproject.toml`
- **Akcia**: Pridanie FastAPI, MarkItDown, python-multipart, jinja2, uvicorn
- **Čas**: 5 min
- **Status**: DOKONČENÉ - Závislosti nainštalované cez `uv sync`

### Krok 1.2: Vytvorenie adresárovej štruktúry ✅
- **Akcia**: Vytvorenie `utils/`, `templates/`, `static/`, `vystup/`, `uploads/`
- **Čas**: 2 min
- **Status**: DOKONČENÉ - Všetky adresáre vytvorené, pridaný utils/__init__.py

## Fáza 2: Základná aplikácia
### Krok 2.1: FastAPI setup
- **Súbor**: `main.py`
- **Akcia**: Základná FastAPI aplikácia s static files handling
- **Funkcionalita**: Root endpoint, health check
- **Čas**: 10 min

### Krok 2.2: HTML šablóny
- **Súbor**: `templates/index.html`
- **Akcia**: Upload formulár s Bootstrap UI
- **Funkcionalita**: File input, directory selector, submit button
- **Čas**: 15 min

### Krok 2.3: CSS styling
- **Súbor**: `static/css/style.css`
- **Akcia**: Vlastné štýly pre lepší vzhľad
- **Čas**: 10 min

## Fáza 3: Konverzia logika
### Krok 3.1: MarkItDown wrapper
- **Súbor**: `utils/converter.py`
- **Akcia**: Trieda pre konverziu dokumentov
- **Funkcionalita**: convert_document(), get_supported_formats()
- **Čas**: 20 min

### Krok 3.2: File handling utilities
- **Súbor**: `utils/file_handler.py`
- **Akcia**: Správa súborov a adresárov
- **Funkcionalita**: save_uploaded_file(), create_output_dir(), cleanup_temp()
- **Čas**: 15 min

## Fáza 4: Web endpoints
### Krok 4.1: Upload endpoint
- **Súbor**: `main.py`
- **Akcia**: POST /upload endpoint
- **Funkcionalita**: Príjem súborov, validácia, konverzia
- **Čas**: 25 min

### Krok 4.2: Results handling
- **Súbor**: `templates/success.html`, `templates/error.html`
- **Akcia**: Stránky pre výsledky konverzie
- **Funkcionalita**: Zobrazenie výsledkov, download linky
- **Čas**: 15 min

## Fáza 5: Vylepšenia
### Krok 5.1: JavaScript enhancements
- **Súbor**: `static/js/app.js`
- **Akcia**: Frontend logika pre progress, validation
- **Čas**: 20 min

### Krok 5.2: Error handling
- **Súbor**: Všetky súbory
- **Akcia**: Komplexné error handling
- **Čas**: 15 min

## Fáza 6: Testovanie a finalizácia
### Krok 6.1: Testovanie s rôznymi formátmi
- **Akcia**: Test PDF, DOCX, XLSX, PPTX, obrázkov
- **Čas**: 30 min

### Krok 6.2: Dokumentácia
- **Súbor**: `README.md`
- **Akcia**: Kompletná dokumentácia používania
- **Čas**: 15 min

## Celkový čas: ~3 hodiny

## Poriadok implementácie súborov:
1. `pyproject.toml` - závislosti
2. Adresárová štruktúra
3. `main.py` - základná aplikácia
4. `utils/converter.py` - MarkItDown wrapper
5. `utils/file_handler.py` - file management
6. `templates/index.html` - upload form
7. `static/css/style.css` - styling
8. Upload endpoint v `main.py`
9. `templates/success.html`, `templates/error.html`
10. `static/js/app.js` - JavaScript
11. Testovanie a ladenie
12. `README.md` - dokumentácia