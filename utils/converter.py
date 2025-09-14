"""
MarkItDown wrapper for document conversion to Markdown.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
from markitdown import MarkItDown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentConverter:
    """Wrapper class for MarkItDown document conversion."""
    
    def __init__(self):
        """Initialize the converter."""
        self.markitdown = MarkItDown()
        self.supported_extensions = {
            '.pdf', '.docx', '.pptx', '.xlsx', 
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            '.mp3', '.wav', '.m4a', '.flac',
            '.html', '.htm', '.csv', '.json', '.xml',
            '.zip', '.txt', '.md'
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return list(self.supported_extensions)
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported."""
        extension = Path(file_path).suffix.lower()
        return extension in self.supported_extensions
    
    def convert_document(self, input_path: str) -> Optional[Dict]:
        """
        Convert document to Markdown.
        
        Args:
            input_path (str): Path to input document
            
        Returns:
            Dict with 'success', 'content', 'error' keys
        """
        try:
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'content': None,
                    'error': f'File not found: {input_path}'
                }
            
            if not self.is_supported_format(input_path):
                extension = Path(input_path).suffix.lower()
                return {
                    'success': False,
                    'content': None,
                    'error': f'Unsupported file format: {extension}'
                }
            
            logger.info(f"Converting document: {input_path}")
            result = self.markitdown.convert(input_path)
            
            if result and hasattr(result, 'text_content'):
                logger.info(f"Successfully converted {input_path}")
                return {
                    'success': True,
                    'content': result.text_content,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'content': None,
                    'error': 'MarkItDown returned empty result'
                }
                
        except Exception as e:
            logger.error(f"Error converting {input_path}: {str(e)}")
            return {
                'success': False,
                'content': None,
                'error': str(e)
            }
    
    def convert_to_file(self, input_path: str, output_path: str) -> Dict:
        """
        Convert document and save to file.
        
        Args:
            input_path (str): Path to input document
            output_path (str): Path to output markdown file
            
        Returns:
            Dict with conversion result
        """
        result = self.convert_document(input_path)
        
        if result['success']:
            try:
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                
                logger.info(f"Saved converted content to: {output_path}")
                result['output_path'] = output_path
                
            except Exception as e:
                logger.error(f"Error saving to {output_path}: {str(e)}")
                result['success'] = False
                result['error'] = f"Failed to save file: {str(e)}"
        
        return result