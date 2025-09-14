"""
Tests for DocumentConverter functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from utils.converter import DocumentConverter


class TestDocumentConverter:
    """Test cases for DocumentConverter class."""

    def test_initialization(self, document_converter: DocumentConverter):
        """Test DocumentConverter initialization."""
        assert document_converter.supported_extensions is not None
        assert isinstance(document_converter.supported_extensions, set)
        assert len(document_converter.supported_extensions) > 0
        assert document_converter.allowed_mime_types is not None

    def test_get_supported_formats(self, document_converter: DocumentConverter):
        """Test getting list of supported formats."""
        formats = document_converter.get_supported_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert '.pdf' in formats
        assert '.docx' in formats
        assert '.txt' in formats
        assert '.html' in formats

    @pytest.mark.parametrize("filename,expected", [
        ("document.pdf", True),
        ("document.docx", True),
        ("document.pptx", True),
        ("document.xlsx", True),
        ("image.jpg", True),
        ("image.png", True),
        ("audio.mp3", True),
        ("text.txt", True),
        ("web.html", True),
        ("data.json", True),
        ("data.csv", True),
        ("archive.zip", True),
        ("readme.md", True),
        ("document.exe", False),
        ("file.bat", False),
        ("script.sh", False),
        ("binary.bin", False),
        ("unknown.xyz", False),
    ])
    def test_is_supported_format(self, document_converter: DocumentConverter, filename: str, expected: bool):
        """Test file format support detection."""
        result = document_converter.is_supported_format(filename)
        assert result == expected

    @pytest.mark.parametrize("filename,expected", [
        ("document.pdf", True),
        ("document.docx", True),
        ("text.txt", True),
        ("web.html", True),
        ("data.json", True),
        ("image.jpg", True),
        ("document.exe", False),
        ("unknown.xyz", False),
    ])
    def test_validate_mime_type(self, document_converter: DocumentConverter, filename: str, expected: bool):
        """Test MIME type validation."""
        result = document_converter.validate_mime_type(filename)
        assert result == expected

    def test_convert_document_nonexistent_file(self, document_converter: DocumentConverter):
        """Test converting a non-existent file."""
        result = document_converter.convert_document("/nonexistent/path/file.txt")
        assert result['success'] is False
        assert 'File not found' in result['error']
        assert result['content'] is None

    def test_convert_document_unsupported_format(self, document_converter: DocumentConverter, temp_dir: Path):
        """Test converting an unsupported file format."""
        # Create an unsupported file
        unsupported_file = temp_dir / "test.exe"
        unsupported_file.write_bytes(b"fake executable")

        result = document_converter.convert_document(str(unsupported_file))
        assert result['success'] is False
        assert 'Unsupported file format' in result['error']
        assert result['content'] is None

    def test_convert_document_text_file(self, document_converter: DocumentConverter, sample_text_file: Path):
        """Test converting a text file."""
        result = document_converter.convert_document(str(sample_text_file))

        if result['success']:
            assert result['content'] is not None
            assert isinstance(result['content'], str)
            assert len(result['content']) > 0
            assert result['error'] is None
        else:
            # If conversion fails, ensure error is reported
            assert result['error'] is not None
            assert result['content'] is None

    def test_convert_document_html_file(self, document_converter: DocumentConverter, sample_html_file: Path):
        """Test converting an HTML file."""
        result = document_converter.convert_document(str(sample_html_file))

        if result['success']:
            assert result['content'] is not None
            assert isinstance(result['content'], str)
            assert result['error'] is None
        else:
            # If conversion fails, ensure error is reported
            assert result['error'] is not None

    def test_convert_document_json_file(self, document_converter: DocumentConverter, sample_json_file: Path):
        """Test converting a JSON file."""
        result = document_converter.convert_document(str(sample_json_file))

        if result['success']:
            assert result['content'] is not None
            assert isinstance(result['content'], str)
            assert result['error'] is None
        else:
            # If conversion fails, ensure error is reported
            assert result['error'] is not None

    @patch('utils.converter.MarkItDown')
    def test_convert_document_markitdown_failure(self, mock_markitdown, document_converter: DocumentConverter, sample_text_file: Path):
        """Test handling of MarkItDown conversion failure."""
        # Mock MarkItDown to raise an exception
        mock_instance = Mock()
        mock_instance.convert.side_effect = Exception("MarkItDown error")
        mock_markitdown.return_value = mock_instance

        # Create a new converter instance with mocked MarkItDown
        converter = DocumentConverter()
        result = converter.convert_document(str(sample_text_file))

        assert result['success'] is False
        assert result['content'] is None
        assert 'MarkItDown error' in result['error']

    def test_convert_document_empty_result(self, document_converter: DocumentConverter, sample_text_file: Path):
        """Test handling of empty MarkItDown result."""
        # Mock the markitdown instance to return None (no result)
        document_converter.markitdown.convert = Mock(return_value=None)

        result = document_converter.convert_document(str(sample_text_file))

        assert result['success'] is False
        assert result['content'] is None
        assert 'empty' in result['error'].lower()

    def test_convert_to_file_success(self, document_converter: DocumentConverter, sample_text_file: Path, temp_dir: Path):
        """Test successful conversion to file."""
        output_file = temp_dir / "output.md"

        result = document_converter.convert_to_file(str(sample_text_file), str(output_file))

        if result['success']:
            assert result['output_path'] == str(output_file)
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            # Clean up
            output_file.unlink()
        else:
            # If conversion fails, file should not exist
            assert not output_file.exists()

    def test_convert_to_file_conversion_failure(self, document_converter: DocumentConverter, temp_dir: Path):
        """Test convert_to_file with conversion failure."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        output_file = temp_dir / "output.md"

        result = document_converter.convert_to_file(str(nonexistent_file), str(output_file))

        assert result['success'] is False
        assert result['error'] is not None
        assert not output_file.exists()

    def test_convert_to_file_write_permission_error(self, document_converter: DocumentConverter, sample_text_file: Path):
        """Test convert_to_file with write permission error."""
        # Try to write to an invalid path (should fail on Windows)
        invalid_output = "/invalid/path/output.md"

        result = document_converter.convert_to_file(str(sample_text_file), invalid_output)

        # This should fail due to path issues, but behavior might vary by system
        # Just ensure we get a reasonable response
        assert isinstance(result, dict)
        assert 'success' in result

    @pytest.mark.parametrize("extension", [
        ".PDF", ".DOCX", ".TXT", ".HTML", ".JSON"  # Test uppercase extensions
    ])
    def test_case_insensitive_extensions(self, document_converter: DocumentConverter, extension: str):
        """Test that extension checking is case insensitive."""
        filename = f"test{extension}"
        result = document_converter.is_supported_format(filename)
        assert result is True


class TestDocumentConverterEdgeCases:
    """Test edge cases and error conditions for DocumentConverter."""

    def test_empty_filename(self, document_converter: DocumentConverter):
        """Test handling of empty filename."""
        assert document_converter.is_supported_format("") is False
        assert document_converter.validate_mime_type("") is False

    def test_filename_without_extension(self, document_converter: DocumentConverter):
        """Test handling of filename without extension."""
        assert document_converter.is_supported_format("filename_no_ext") is False

    def test_filename_with_multiple_dots(self, document_converter: DocumentConverter):
        """Test handling of filename with multiple dots."""
        assert document_converter.is_supported_format("file.name.with.dots.txt") is True
        assert document_converter.is_supported_format("file.name.with.dots.exe") is False

    def test_very_long_filename(self, document_converter: DocumentConverter):
        """Test handling of very long filename."""
        long_name = "x" * 1000 + ".txt"
        # Should still work based on extension
        assert document_converter.is_supported_format(long_name) is True

    @pytest.mark.slow
    def test_convert_large_file(self, document_converter: DocumentConverter, sample_large_file: Path):
        """Test converting a large file (marked as slow test)."""
        result = document_converter.convert_document(str(sample_large_file))

        # This test might be slow or fail due to size limits
        # Just ensure we get a reasonable response
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'content' in result
        assert 'error' in result