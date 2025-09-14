# MDitD - MarkItDown Web Aplikácia

Rýchla web aplikácia na konverziu dokumentov do Markdown formátu pomocou Microsoft MarkItDown.

## Súbory projektu

### Plánovacie dokumenty
- **`PLAN.md`** - Kompletný plán projektu, technický stack, atruktúra
- **`DEVELOPMENT_STEPS.md`** - Detailný postup vývoja po krokoch s asovými odhadmi

### Hlavné súbory aplikácie
- **`main.py`** - FastAPI aplikácia, hlavný entry point
- **`pyproject.toml`** - Python projekt konfigurácia a závislosti

### Aplikaná logika (utils/)
- **`utils/converter.py`** - MarkItDown konverzia logika
- **`utils/file_handler.py`** - Správa súborov a adresárov

### Frontend (templates/ a static/)
- **`templates/index.html`** - Hlavná stránka s upload formulárom
- **`templates/success.html`** - Stránka úspeanej konverzie
- **`templates/error.html`** - Error handling stránka
- **`static/css/style.css`** - Vlastné CSS atýly
- **`static/js/app.js`** - Frontend JavaScript

### Pracovné adresáre
- **`vystup/`** - Default adresár pre MD výstupné súbory
- **`uploads/`** - Doasný adresár pre nahraté súbory

## Podporované formáty
PDF, Word, Excel, PowerPoint, obrázky, audio, HTML, CSV, JSON, XML, ZIP

## Spustenie
```bash
uv add fastapi markitdown python-multipart jinja2 uvicorn
uvicorn main:app --reload
```