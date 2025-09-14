# MDitD - Návrhy vylepšení

Komprehenzívna analýza kódovej bázy s návrhmi na zlepšenie výkonu, stability, bezpečnosti a čistoty kódu.

## 🚀 1. Vylepšenia výkonu

### 1.1 Správa pamäte
**Problém**: Celý obsah súboru sa načítava do pamäte naraz (`main.py:64`)
```python
file_content = await file.read()  # Problematické pre veľké súbory
```

**Riešenie**: Implementovať streaming upload pre veľké súbory
```python
async def save_file_stream(file: UploadFile, file_path: str, chunk_size: int = 8192):
    """Streamovať súbor na disk bez načítania do pamäte."""
    with open(file_path, 'wb') as f:
        while chunk := await file.read(chunk_size):
            f.write(chunk)
```

### 1.2 Chýbajúce async/await optimalizácie
**Problém**: File operácie v `utils/file_handler.py` sú synchrónne, blokujú event loop

**Riešenie**: Použiť `aiofiles` pre async file operácie
```bash
uv add aiofiles
```

```python
import aiofiles
import aiofiles.os

async def save_uploaded_file_async(self, file: UploadFile, filename: str) -> str:
    """Async verzia save_uploaded_file."""
    safe_filename = self._sanitize_filename(filename)
    file_path = self.uploads_dir / safe_filename
    
    counter = 1
    while await aiofiles.os.path.exists(file_path):
        name_part = Path(safe_filename).stem
        ext_part = Path(safe_filename).suffix
        new_filename = f"{name_part}_{counter}{ext_part}"
        file_path = self.uploads_dir / new_filename
        counter += 1
    
    async with aiofiles.open(file_path, 'wb') as f:
        async for chunk in file.stream():
            await f.write(chunk)
    
    return str(file_path)
```

### 1.3 Neefektívny loop spracovania súborov
**Problém**: Súbory sa spracovávajú sekvenčne

**Riešenie**: Spracovávať súbory concurrent
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def upload_files(files: List[UploadFile] = File(...)):
    with ThreadPoolExecutor(max_workers=min(4, len(files))) as executor:
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                executor, process_single_file, file, output_dir
            ) for file in files
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return format_results(results, files)
```

## 🛡️ 2. Vylepšenia stability

### 2.1 Chýba validácia veľkosti súborov
**Problém**: Žiadne limity na veľkosť súborov

**Riešenie**: Pridať validáciu veľkosti
```python
# Konštanty
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    # Validovať celkovú veľkosť
    total_size = sum(getattr(file, 'size', 0) for file in files)
    if total_size > MAX_TOTAL_SIZE:
        raise HTTPException(413, "Celková veľkosť súborov presahuje limit")
    
    for file in files:
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(413, f"Súbor {file.filename} presahuje limit veľkosti")
```

### 2.2 Neúplné error handling
**Problém**: Generické exception handling maskuje špecifické chyby

**Riešenie**: Implementovať špecifické exception handling
```python
try:
    # Konverzia logika
    pass
except FileNotFoundError:
    error = "Dočasný súbor bol neočakávane zmazaný"
except PermissionError:
    error = "Odmietnutý prístup k súboru"
except OSError as e:
    error = f"Systémová chyba: {e.strerror}"
except Exception as e:
    logger.exception(f"Neočakávaná chyba pri spracovaní {file.filename}")
    error = "Interná chyba servera"
```

### 2.3 Problémy s cleanup zdrojov
**Riešenie**: Použiť context managery
```python
import contextlib

@contextlib.contextmanager
def temporary_file(content: bytes, filename: str):
    """Context manager pre dočasné súbory."""
    temp_path = None
    try:
        temp_path = file_handler.save_uploaded_file(content, filename)
        yield temp_path
    finally:
        if temp_path and Path(temp_path).exists():
            file_handler.cleanup_temp_file(temp_path)
```

## 🔒 3. Vylepšenia bezpečnosti

### 3.1 Path traversal zraniteľnosti
**Problém**: Nedostatočná sanitizácia filename

**Riešenie**: Posilniť filename sanitization
```python
import re

def _sanitize_filename(self, filename: str) -> str:
    """Vylepšená sanitizácia filename."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    filename = filename.strip('. ')
    
    # Zabrániť rezervovaným menám (Windows)
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                     'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                     'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 
                     'LPT7', 'LPT8', 'LPT9'}
    
    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        filename = f"file_{filename}"
    
    if len(filename) > 255:
        stem = Path(filename).stem[:200]
        suffix = Path(filename).suffix
        filename = f"{stem}{suffix}"
    
    return filename or "unnamed_file"
```

### 3.2 Chýba MIME type validácia
**Riešenie**: Pridať MIME type validáciu
```python
import mimetypes

class DocumentConverter:
    def __init__(self):
        self.allowed_mime_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/html', 'text/csv', 'application/json', 'text/plain'
            # ... ďalšie podporované typy
        }
    
    async def validate_file_content(self, file: UploadFile) -> bool:
        """Validovať obsah súboru podľa MIME typu."""
        detected_type = mimetypes.guess_type(file.filename)[0]
        return detected_type in self.allowed_mime_types
```

### 3.3 Output directory traversal
**Riešenie**: Bezpečná validácia output path
```python
def create_output_path(self, original_filename: str, output_dir: Optional[str] = None) -> str:
    """Vytvoriť bezpečný output path."""
    if output_dir:
        target_dir = Path(output_dir).resolve()
        base_dir = Path.cwd().resolve()
        try:
            target_dir.relative_to(base_dir)
        except ValueError:
            raise ValueError(f"Output adresár mimo povolenú cestu: {target_dir}")
    else:
        target_dir = self.output_dir.resolve()
    
    # Zvyšok metódy...
```

## 🧹 4. Vylepšenia čistoty kódu

### 4.1 Chýbajúce type hints
**Riešenie**: Pridať komprehenzívne type hints
```python
from typing import List, Optional, Dict, Any

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    output_dir: Optional[str] = Form("vystup")
) -> Dict[str, Any]:
    """Upload a konverzia dokumentov do Markdown."""
    results: List[Dict[str, Any]] = []
    # ...
```

### 4.2 Magic numbers a chýbajúce konštanty
**Riešenie**: Definovať konštanty v `config.py`
```python
# config.py
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB
UPLOAD_CHUNK_SIZE = 8192
DEFAULT_UPLOADS_DIR = "uploads"
DEFAULT_OUTPUT_DIR = "vystup"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8001

SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx', 
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
    '.mp3', '.wav', '.m4a', '.flac',
    '.html', '.htm', '.csv', '.json', '.xml',
    '.zip', '.txt', '.md'
}
```

### 4.3 Chýbajúce docstrings
**Riešenie**: Štandardizovať docstrings
```python
def convert_to_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Konvertovať dokument a uložiť do súboru.
    
    Args:
        input_path: Absolútna cesta k vstupnému dokumentu
        output_path: Absolútna cesta kam sa uloží markdown súbor
        
    Returns:
        Dictionary obsahujúci:
            - success (bool): Či bola konverzia úspešná
            - content (str|None): Konvertovaný markdown obsah
            - error (str|None): Chybová správa ak konverzia zlyhala
            - output_path (str|None): Cesta k uloženému súboru ak úspešná
            
    Raises:
        OSError: Ak file system operácie zlyhajú
        PermissionError: Ak chýbajú oprávnenia na čítanie/zápis súborov
    """
```

### 4.4 Problém s logging konfiguráciou
**Riešenie**: Centralizovaná logging konfigurácia
```python
# logging_config.py
import logging
import sys

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Konfigurovať aplikačné logovanie."""
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
```

## ⚙️ 5. Ďalšie odporúčania

### 5.1 Configuration management
**Riešenie**: Použiť environment-based konfiguráciu
```python
# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Aplikačné nastavenia s podporou environment variables."""
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = True
    max_file_size: int = 100 * 1024 * 1024
    max_total_size: int = 500 * 1024 * 1024
    uploads_dir: str = "uploads"
    output_dir: str = "vystup"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 5.2 Vylepšený health check
```python
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Vylepšený health check so system statusom."""
    return {
        "status": "healthy",
        "service": "MDitD",
        "version": "0.1.0",
        "timestamp": time.time(),
        "components": {
            "converter": converter_status,
            "filesystem": fs_status
        }
    }
```

### 5.3 Testing štruktúra
**Riešenie**: Pridať komprehenzívne testy
```bash
uv add pytest pytest-asyncio httpx
mkdir tests
```

```python
# tests/test_converter.py
import pytest
from utils.converter import DocumentConverter

class TestDocumentConverter:
    @pytest.fixture
    def converter(self):
        return DocumentConverter()
    
    def test_supported_formats(self, converter):
        assert converter.is_supported_format("test.pdf")
        assert not converter.is_supported_format("test.exe")
```

## 📊 Súhrn

### ✅ IMPLEMENTOVANÉ (Krok 1 - Bezpečnosť):
1. **✅ Vylepšená filename sanitization** - Regex-based sanitization, kontrola rezervovaných mien, limit dĺžky
2. **✅ MIME type validácia** - Validácia na základe MIME typu okrem extension check
3. **✅ Bezpečná output path validácia** - Path traversal ochrana, relative path kontrola
4. **✅ File size validácia** - Limity 100MB/súbor, 500MB celkovo
5. **✅ Konštanty v config.py** - Centralizované nastavenia

### ✅ IMPLEMENTOVANÉ (Krok 2 - Stabilita):
1. **✅ Špecifické error handling** - Nahradené generic Exception s FileNotFoundError, PermissionError, OSError
2. **✅ Resource cleanup s context managers** - Automatické čistenie temporary files
3. **✅ Vylepšené error messages** - Popisné chyby s podporovanými formátmi a možnými riešeniami
4. **✅ Rozšírená input validácia** - Validácia počtu súborov, dĺžky filename, zakázané znaky
5. **✅ Testované všetky stability improvements** - Path traversal, multiple files, error conditions

### 🔄 ZOSTÁVA IMPLEMENTOVAŤ:
3. **Výkon**: Pridať async file handling a concurrent processing  
4. **Organizácia kódu a dokumentácia**

### Odporúčané poradie priority:
1. **✅ Bezpečnostné vylepšenia** - DOKONČENÉ
2. **✅ Error handling a validácia** - DOKONČENÉ
3. **🔄 Výkonové optimalizácie**
4. **🔄 Organizácia kódu a dokumentácia**

### Odhadovaný zostávajúci čas implementácie:
- ~~Bezpečnostné opravy: 1-2 dni~~ ✅ DOKONČENÉ
- ~~Stability vylepšenia: 1 deň~~ ✅ DOKONČENÉ
- Výkonové vylepšenia: 2-3 dni
- Code cleanup: 1-2 dni  
- Testovanie: 1-2 dni (menej potrebné vďaka postupnému testovaniu)

**Prvé dve fázy (Bezpečnosť a Stabilita) sú kompletné a testované!** Aplikácia má teraz výrazne lepšiu bezpečnosť, error handling a resource management.