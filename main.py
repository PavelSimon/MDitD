from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import os
from utils.converter import DocumentConverter
from utils.file_handler import FileHandler
from config import MAX_FILE_SIZE, MAX_TOTAL_SIZE

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
    # Validate total size and individual file sizes
    total_size = 0
    for file in files:
        if hasattr(file, 'size') and file.size:
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File {file.filename} ({file.size:,} bytes) exceeds maximum size limit ({MAX_FILE_SIZE:,} bytes)"
                )
            total_size += file.size
    
    if total_size > MAX_TOTAL_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Total upload size ({total_size:,} bytes) exceeds limit ({MAX_TOTAL_SIZE:,} bytes)"
        )
    
    results = []
    
    for file in files:
        try:
            # Validate file
            if not file.filename:
                results.append({
                    "filename": "unknown",
                    "success": False,
                    "error": "No filename provided"
                })
                continue
            
            # Check if format is supported
            if not converter.is_supported_format(file.filename):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Unsupported file format"
                })
                continue
            
            # Validate MIME type for additional security
            if not converter.validate_mime_type(file.filename):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"File type validation failed"
                })
                continue
            
            # Save uploaded file
            file_content = await file.read()
            temp_path = file_handler.save_uploaded_file(file_content, file.filename)
            
            # Create output path with security validation
            try:
                output_path = file_handler.create_output_path(file.filename, output_dir)
            except ValueError as e:
                file_handler.cleanup_temp_file(temp_path)
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Invalid output directory: {str(e)}"
                })
                continue
            
            # Convert document
            result = converter.convert_to_file(temp_path, output_path)
            
            # Clean up temporary file
            file_handler.cleanup_temp_file(temp_path)
            
            # Add to results
            results.append({
                "filename": file.filename,
                "success": result['success'],
                "error": result.get('error'),
                "output_path": result.get('output_path') if result['success'] else None
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename if hasattr(file, 'filename') else "unknown",
                "success": False,
                "error": str(e)
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
