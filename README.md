# MDitD - MarkItDown Web Aplik�cia

R�chla web aplik�cia na konverziu dokumentov do Markdown form�tu pomocou Microsoft MarkItDown.

## S�bory projektu

### Pl�novacie dokumenty
- **`PLAN.md`** - Kompletn� pl�n projektu, technick� stack, atrukt�ra
- **`DEVELOPMENT_STEPS.md`** - Detailn� postup v�voja po krokoch s asov�mi odhadmi

### Hlavn� s�bory aplik�cie
- **`main.py`** - FastAPI aplik�cia, hlavn� entry point
- **`pyproject.toml`** - Python projekt konfigur�cia a z�vislosti

### Aplikan� logika (utils/)
- **`utils/converter.py`** - MarkItDown konverzia logika
- **`utils/file_handler.py`** - Spr�va s�borov a adres�rov

### Frontend (templates/ a static/)
- **`templates/index.html`** - Hlavn� str�nka s upload formul�rom
- **`templates/success.html`** - Str�nka �speanej konverzie
- **`templates/error.html`** - Error handling str�nka
- **`static/css/style.css`** - Vlastn� CSS at�ly
- **`static/js/app.js`** - Frontend JavaScript

### Pracovn� adres�re
- **`vystup/`** - Default adres�r pre MD v�stupn� s�bory
- **`uploads/`** - Doasn� adres�r pre nahrat� s�bory

## Podporovan� form�ty
PDF, Word, Excel, PowerPoint, obr�zky, audio, HTML, CSV, JSON, XML, ZIP

## Spustenie
```bash
# Inštalácia závislostí
uv sync

# Spustenie aplikácie
uv run python main.py

# Alebo priamo cez uvicorn
uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Aplikácia beží na: **http://localhost:8001**

## Použitie
1. Otvorte browser a navigujte na http://localhost:8001
2. Vyberte súbory na konverziu (podporované: PDF, Word, Excel, PowerPoint, obrázky, audio, HTML, CSV, JSON, XML, ZIP)
3. Vyberte cieľový adresár (default: `vystup/`)
4. Kliknite "Convert to Markdown"
5. Markdown súbory sa uložia do vybraného adresára

## Testované formáty
- ✅ TXT files - basic text conversion
- ✅ HTML files - kompletná konverzia s headings, lists, links, code blocks