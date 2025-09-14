# MDitD - MarkItDown Web Aplikácia

Rýchla web aplikácia na konverziu dokumentov do Markdown formátu pomocou Microsoft MarkItDown.

## Súbory projektu

### Plánovacie dokumenty
- **`PLAN.md`** - Kompletný plán projektu, technický stack, štruktúra
- **`DEVELOPMENT_STEPS.md`** - Detailný postup vývoja po krokoch s časovými odhadmi

### Hlavné súbory aplikácie
- **`main.py`** - FastAPI aplikácia, hlavný entry point
- **`pyproject.toml`** - Python projekt konfigurácia a závislosti

### Aplikačná logika (utils/)
- **`utils/converter.py`** - MarkItDown konverzia logika
- **`utils/file_handler.py`** - Správa súborov a adresárov

### Frontend (templates/ a static/)
- **`templates/index.html`** - Hlavná stránka s upload formulárom
- **`templates/success.html`** - Stránka úspešnej konverzie
- **`templates/error.html`** - Error handling stránka
- **`static/css/style.css`** - Vlastné CSS štýly
- **`static/js/app.js`** - Frontend JavaScript

### Pracovné adresáre
- **`vystup/`** - Default adresár pre MD výstupné súbory
- **`uploads/`** - Dočasný adresár pre nahraté súbory

## Podporované formáty
PDF, Word, Excel, PowerPoint, obrázky, audio, HTML, CSV, JSON, XML, ZIP

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