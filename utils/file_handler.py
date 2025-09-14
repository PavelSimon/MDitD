"""
File handling utilities for MDitD application.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file operations for the application."""
    
    def __init__(self, uploads_dir: str = "uploads", output_dir: str = "vystup"):
        """
        Initialize file handler.
        
        Args:
            uploads_dir (str): Directory for temporary uploads
            output_dir (str): Default output directory
        """
        self.uploads_dir = Path(uploads_dir)
        self.output_dir = Path(output_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.uploads_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Directories ensured: {self.uploads_dir}, {self.output_dir}")
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to temporary directory.
        
        Args:
            file_content (bytes): File content
            filename (str): Original filename
            
        Returns:
            str: Path to saved file
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)
        file_path = self.uploads_dir / safe_filename
        
        # Handle duplicate filenames
        counter = 1
        while file_path.exists():
            name_part = Path(safe_filename).stem
            ext_part = Path(safe_filename).suffix
            new_filename = f"{name_part}_{counter}{ext_part}"
            file_path = self.uploads_dir / new_filename
            counter += 1
        
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            logger.info(f"Saved uploaded file: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal."""
        # Remove path components and keep only filename
        filename = os.path.basename(filename)
        
        # Replace problematic characters
        problematic_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in problematic_chars:
            filename = filename.replace(char, '_')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"
            
        return filename
    
    def create_output_path(self, original_filename: str, 
                          output_dir: Optional[str] = None) -> str:
        """
        Create output path for markdown file.
        
        Args:
            original_filename (str): Original file name
            output_dir (str): Custom output directory
            
        Returns:
            str: Output path for markdown file
        """
        if output_dir:
            target_dir = Path(output_dir)
        else:
            target_dir = self.output_dir
        
        # Ensure output directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Change extension to .md
        base_name = Path(original_filename).stem
        output_filename = f"{base_name}.md"
        output_path = target_dir / output_filename
        
        # Handle duplicate filenames
        counter = 1
        while output_path.exists():
            output_filename = f"{base_name}_{counter}.md"
            output_path = target_dir / output_filename
            counter += 1
        
        return str(output_path)
    
    def cleanup_temp_file(self, file_path: str) -> bool:
        """
        Clean up temporary file.
        
        Args:
            file_path (str): Path to temporary file
            
        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file information.
        
        Args:
            file_path (str): Path to file
            
        Returns:
            dict: File information
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'extension': path.suffix.lower(),
                'exists': path.exists()
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {
                'name': '',
                'size': 0,
                'extension': '',
                'exists': False,
                'error': str(e)
            }
    
    def list_output_files(self, output_dir: Optional[str] = None) -> List[dict]:
        """
        List files in output directory.
        
        Args:
            output_dir (str): Custom output directory
            
        Returns:
            List[dict]: List of file information
        """
        if output_dir:
            target_dir = Path(output_dir)
        else:
            target_dir = self.output_dir
        
        files = []
        try:
            if target_dir.exists():
                for file_path in target_dir.glob('*.md'):
                    files.append(self.get_file_info(str(file_path)))
            return files
        except Exception as e:
            logger.error(f"Error listing files in {target_dir}: {str(e)}")
            return []