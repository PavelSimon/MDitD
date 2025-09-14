from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import os
from pathlib import Path
from utils.converter import DocumentConverter
from utils.file_handler import FileHandler
from config import (
    MAX_FILE_SIZE, MAX_TOTAL_SIZE, MAX_FILES_COUNT, MIN_FILE_SIZE,
    MAX_FILENAME_LENGTH, MAX_OUTPUT_DIR_LENGTH,
    FORBIDDEN_FILENAME_PATTERNS, FORBIDDEN_OUTPUT_DIR_PATTERNS
)

app = FastAPI(
    title="MDitD - MarkItDown Web App",
    description="Convert documents to Markdown via web interface",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize services
converter = DocumentConverter()
file_handler = FileHandler()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MDitD"}

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    output_dir: Optional[str] = Form("vystup")
):
    """Upload and convert documents to Markdown."""
    
    # Validate number of files
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided. Please select at least one file to upload."
        )
    
    if len(files) > MAX_FILES_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files ({len(files)}). Maximum allowed is {MAX_FILES_COUNT} files per upload."
        )
    
    # Validate output directory
    if output_dir:
        if len(output_dir) > MAX_OUTPUT_DIR_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Output directory name too long ({len(output_dir)} characters). Maximum allowed is {MAX_OUTPUT_DIR_LENGTH} characters."
            )
        
        # Check for forbidden patterns in output directory
        for pattern in FORBIDDEN_OUTPUT_DIR_PATTERNS:
            if pattern in output_dir:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid output directory: Contains forbidden pattern '{pattern}'. Please use relative directory names only."
                )
        
        # Check for potentially dangerous paths
        if output_dir.strip().startswith('.'):
            raise HTTPException(
                status_code=400,
                detail="Invalid output directory: Cannot start with dot (.) for security reasons."
            )
    
    # Validate total size and individual file sizes
    total_size = 0
    for file in files:
        if hasattr(file, 'size') and file.size:
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File '{file.filename}' is too large ({file.size:,} bytes). Maximum allowed size is {MAX_FILE_SIZE:,} bytes ({MAX_FILE_SIZE//1024//1024} MB). Please compress or split the file."
                )
            total_size += file.size
    
    if total_size > MAX_TOTAL_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Total upload size ({total_size:,} bytes) exceeds limit ({MAX_TOTAL_SIZE:,} bytes, {MAX_TOTAL_SIZE//1024//1024} MB). Please reduce the number of files or compress them."
        )
    
    results = []
    
    for file in files:
        try:
            # Validate file
            if not file.filename:
                results.append({
                    "filename": "unknown",
                    "success": False,
                    "error": "File upload failed: No filename provided. Please ensure the file has a valid name."
                })
                continue
            
            # Validate filename length
            if len(file.filename) > MAX_FILENAME_LENGTH:
                results.append({
                    "filename": file.filename[:50] + "...",  # Truncate for display
                    "success": False,
                    "error": f"Filename too long ({len(file.filename)} characters). Maximum allowed is {MAX_FILENAME_LENGTH} characters."
                })
                continue
            
            # Check for forbidden characters in filename
            forbidden_chars_found = [pattern for pattern in FORBIDDEN_FILENAME_PATTERNS if pattern in file.filename]
            if forbidden_chars_found:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Filename contains forbidden characters: {', '.join(forbidden_chars_found)}. Please rename the file."
                })
                continue
            
            # Validate file size (individual check within processing loop)
            if hasattr(file, 'size') and file.size is not None:
                if file.size < MIN_FILE_SIZE:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "File is empty or corrupted. Please select a valid file."
                    })
                    continue
            
            # Check if format is supported
            if not converter.is_supported_format(file.filename):
                supported_formats = ', '.join(converter.get_supported_formats())
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Unsupported file format '{Path(file.filename).suffix}'. Supported formats: {supported_formats}"
                })
                continue
            
            # Validate MIME type for additional security
            if not converter.validate_mime_type(file.filename):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Security validation failed: File type '{Path(file.filename).suffix}' does not match expected MIME type. This may indicate file corruption or security risk."
                })
                continue
            
            # Save uploaded file and process with context manager
            file_content = await file.read()
            
            # Create output path with security validation
            try:
                output_path = file_handler.create_output_path(file.filename, output_dir)
            except ValueError as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Output directory error: {str(e)}. Please use a valid directory path within the current project."
                })
                continue
            
            # Use context manager for safe temporary file handling
            with file_handler.temporary_file(file_content, file.filename) as temp_path:
                # Convert document
                result = converter.convert_to_file(temp_path, output_path)
                
                # Add to results
                results.append({
                    "filename": file.filename,
                    "success": result['success'],
                    "error": result.get('error'),
                    "output_path": result.get('output_path') if result['success'] else None
                })
            
        except FileNotFoundError:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Processing error: Temporary file was deleted unexpectedly. This may be caused by antivirus software or insufficient disk space."
            })
        except PermissionError:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Permission error: Cannot access file. Please check if the file is locked by another application or if you have sufficient permissions."
            })
        except OSError as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"System error: {e.strerror if hasattr(e, 'strerror') else str(e)}. This may be due to insufficient disk space, file corruption, or system limitations."
            })
        except Exception as e:
            # Context manager handles cleanup automatically
            results.append({
                "filename": file.filename if hasattr(file, 'filename') else "unknown",
                "success": False,
                "error": "An unexpected error occurred during processing. Please try again or contact support if the problem persists."
            })
    
    return JSONResponse(content={
        "results": results,
        "total_files": len(files),
        "successful": len([r for r in results if r['success']]),
        "failed": len([r for r in results if not r['success']])
    })

@app.get("/formats")
async def get_supported_formats():
    """Get list of supported file formats."""
    return {"supported_formats": converter.get_supported_formats()}

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    main()
