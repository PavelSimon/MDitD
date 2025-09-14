"""
Tests for FileHandler functionality.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from fastapi import UploadFile
from io import BytesIO

from utils.file_handler import FileHandler


class TestFileHandler:
    """Test cases for FileHandler class."""

    def test_initialization(self, file_handler: FileHandler):
        """Test FileHandler initialization."""
        assert file_handler.uploads_dir.exists()
        assert file_handler.output_dir.exists()

    def test_ensure_directories(self, temp_dir: Path):
        """Test directory creation."""
        uploads_dir = temp_dir / "new_uploads"
        output_dir = temp_dir / "new_output"

        # Directories should not exist initially
        assert not uploads_dir.exists()
        assert not output_dir.exists()

        # Create FileHandler - should create directories
        handler = FileHandler(uploads_dir=str(uploads_dir), output_dir=str(output_dir))

        assert handler.uploads_dir.exists()
        assert handler.output_dir.exists()

    @pytest.mark.parametrize("filename,expected", [
        # Basic cases
        ("normal_file.txt", "normal_file.txt"),
        ("file with spaces.txt", "file with spaces.txt"),

        # Path traversal attempts
        ("../../../etc/passwd", "passwd"),
        ("..\\..\\windows\\system32\\config", "config"),
        ("subdir/file.txt", "file.txt"),

        # Dangerous characters
        ("file<>:\"|?*.txt", "file_______.txt"),
        ("file\x00\x01\x02.txt", "file.txt"),

        # Windows reserved names
        ("CON.txt", "file_CON.txt"),
        ("PRN.docx", "file_PRN.docx"),
        ("AUX", "file_AUX"),
        ("NUL.pdf", "file_NUL.pdf"),
        ("COM1.txt", "file_COM1.txt"),
        ("LPT1.doc", "file_LPT1.doc"),

        # Edge cases
        ("", "unnamed_file"),
        ("...", "unnamed_file"),
        ("   ", "unnamed_file"),
        (" . . . ", "unnamed_file"),

        # Long filename
        ("x" * 300 + ".txt", "x" * 200 + ".txt"),

        # Leading/trailing problematic chars
        (".hidden_file.txt", "hidden_file.txt"),
        ("file.txt.", "file.txt"),
        ("  file.txt  ", "file.txt"),
    ])
    def test_sanitize_filename(self, file_handler: FileHandler, filename: str, expected: str):
        """Test filename sanitization."""
        result = file_handler._sanitize_filename(filename)
        assert result == expected

    def test_save_uploaded_file(self, file_handler: FileHandler):
        """Test saving uploaded file."""
        content = b"Hello, World!"
        filename = "test.txt"

        file_path = file_handler.save_uploaded_file(content, filename)

        assert Path(file_path).exists()
        assert Path(file_path).read_bytes() == content
        assert Path(file_path).name == filename

        # Cleanup
        Path(file_path).unlink()

    def test_save_uploaded_file_duplicate_names(self, file_handler: FileHandler):
        """Test handling of duplicate filenames."""
        content1 = b"Content 1"
        content2 = b"Content 2"
        filename = "duplicate.txt"

        # Save first file
        file_path1 = file_handler.save_uploaded_file(content1, filename)
        assert Path(file_path1).exists()
        assert Path(file_path1).name == filename

        # Save second file with same name
        file_path2 = file_handler.save_uploaded_file(content2, filename)
        assert Path(file_path2).exists()
        assert Path(file_path2).name == "duplicate_1.txt"

        # Verify contents are different
        assert Path(file_path1).read_bytes() == content1
        assert Path(file_path2).read_bytes() == content2

        # Cleanup
        Path(file_path1).unlink()
        Path(file_path2).unlink()

    def test_create_output_path(self, file_handler: FileHandler):
        """Test creating output paths."""
        filename = "document.pdf"
        output_path = file_handler.create_output_path(filename)

        assert output_path.endswith("document.md")
        assert Path(output_path).parent == file_handler.output_dir

    def test_create_output_path_custom_dir(self, file_handler: FileHandler):
        """Test creating output paths with custom directory."""
        filename = "document.pdf"
        custom_dir = "custom_output"

        output_path = file_handler.create_output_path(filename, custom_dir)

        assert output_path.endswith("document.md")
        assert custom_dir in output_path

    def test_create_output_path_security_validation(self, file_handler: FileHandler):
        """Test output path security validation."""
        filename = "document.pdf"

        # Test path traversal attempt
        with pytest.raises(ValueError, match="Output directory outside allowed path"):
            file_handler.create_output_path(filename, "../../../dangerous")

        # Test absolute path attempt
        with pytest.raises(ValueError, match="Output directory outside allowed path"):
            file_handler.create_output_path(filename, "/etc/passwd")

    def test_create_output_path_duplicate_handling(self, file_handler: FileHandler):
        """Test handling of duplicate output filenames."""
        filename = "document.pdf"

        # Create first output path and file
        output_path1 = file_handler.create_output_path(filename)
        Path(output_path1).touch()

        # Create second output path - should get incremented name
        output_path2 = file_handler.create_output_path(filename)

        assert output_path1 != output_path2
        assert "document.md" in output_path1
        assert "document_1.md" in output_path2

        # Cleanup
        Path(output_path1).unlink()

    def test_cleanup_temp_file(self, file_handler: FileHandler):
        """Test cleaning up temporary files."""
        # Create a temporary file
        content = b"temporary content"
        file_path = file_handler.save_uploaded_file(content, "temp.txt")
        assert Path(file_path).exists()

        # Clean up the file
        result = file_handler.cleanup_temp_file(file_path)
        assert result is True
        assert not Path(file_path).exists()

    def test_cleanup_temp_file_nonexistent(self, file_handler: FileHandler):
        """Test cleaning up non-existent file."""
        result = file_handler.cleanup_temp_file("/nonexistent/file.txt")
        assert result is True  # Should not fail on non-existent files

    def test_get_file_info(self, file_handler: FileHandler, sample_text_file: Path):
        """Test getting file information."""
        info = file_handler.get_file_info(str(sample_text_file))

        assert info['name'] == sample_text_file.name
        assert info['size'] > 0
        assert info['extension'] == '.txt'
        assert info['exists'] is True

    def test_get_file_info_nonexistent(self, file_handler: FileHandler):
        """Test getting info for non-existent file."""
        info = file_handler.get_file_info("/nonexistent/file.txt")

        assert 'error' in info
        assert info['exists'] is False

    def test_list_output_files(self, file_handler: FileHandler):
        """Test listing output files."""
        # Create some test markdown files
        (file_handler.output_dir / "test1.md").write_text("content1")
        (file_handler.output_dir / "test2.md").write_text("content2")
        (file_handler.output_dir / "other.txt").write_text("other")  # Should be ignored

        files = file_handler.list_output_files()

        assert len(files) == 2
        filenames = [f['name'] for f in files]
        assert "test1.md" in filenames
        assert "test2.md" in filenames
        assert "other.txt" not in filenames

        # Cleanup
        (file_handler.output_dir / "test1.md").unlink()
        (file_handler.output_dir / "test2.md").unlink()
        (file_handler.output_dir / "other.txt").unlink()

    def test_temporary_file_context_manager(self, file_handler: FileHandler):
        """Test temporary file context manager."""
        content = b"test content"
        filename = "context_test.txt"

        with file_handler.temporary_file(content, filename) as temp_path:
            # File should exist within context
            assert Path(temp_path).exists()
            assert Path(temp_path).read_bytes() == content

        # File should be cleaned up after context
        assert not Path(temp_path).exists()

    def test_temporary_file_context_manager_exception(self, file_handler: FileHandler):
        """Test temporary file context manager with exception."""
        content = b"test content"
        filename = "exception_test.txt"

        try:
            with file_handler.temporary_file(content, filename) as temp_path:
                # File should exist within context
                assert Path(temp_path).exists()
                # Raise an exception to test cleanup
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected

        # File should still be cleaned up after exception
        assert not Path(temp_path).exists()


class TestFileHandlerAsync:
    """Test cases for FileHandler async methods."""

    @pytest.mark.asyncio
    async def test_save_uploaded_file_async(self, file_handler: FileHandler):
        """Test async file saving."""
        content = b"Hello, Async World!"
        filename = "async_test.txt"

        # Mock UploadFile
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(side_effect=[content[:10], content[10:], b""])

        file_path = await file_handler.save_uploaded_file_async(mock_file, filename)

        assert Path(file_path).exists()
        assert Path(file_path).read_bytes() == content

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_stream_file_chunks(self, file_handler: FileHandler):
        """Test file streaming in chunks."""
        content = b"0123456789" * 100  # 1000 bytes
        mock_file = Mock(spec=UploadFile)

        # Mock reading in chunks
        chunk_size = 100
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        chunks.append(b"")  # End of file

        mock_file.read = AsyncMock(side_effect=chunks)
        mock_file.seek = AsyncMock()

        # Collect chunks
        collected_chunks = []
        async for chunk in file_handler._stream_file_chunks(mock_file, chunk_size):
            collected_chunks.append(chunk)

        # Verify all content was streamed
        reconstructed = b"".join(collected_chunks)
        assert reconstructed == content

        # Verify file was reset
        mock_file.seek.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_save_file_stream_async(self, file_handler: FileHandler, temp_dir: Path):
        """Test streaming file to disk."""
        content = b"Stream content test"
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(side_effect=[content, b""])
        mock_file.seek = AsyncMock()

        output_path = temp_dir / "streamed.txt"

        await file_handler.save_file_stream_async(mock_file, str(output_path))

        assert output_path.exists()
        assert output_path.read_bytes() == content

    @pytest.mark.asyncio
    async def test_cleanup_temp_file_async(self, file_handler: FileHandler):
        """Test async file cleanup."""
        # Create a temporary file
        content = b"async cleanup test"
        file_path = file_handler.save_uploaded_file(content, "async_cleanup.txt")
        assert Path(file_path).exists()

        # Clean up async
        result = await file_handler.cleanup_temp_file_async(file_path)
        assert result is True
        assert not Path(file_path).exists()

    @pytest.mark.asyncio
    async def test_get_file_info_async(self, file_handler: FileHandler, sample_text_file: Path):
        """Test async file info retrieval."""
        info = await file_handler.get_file_info_async(str(sample_text_file))

        assert info['name'] == sample_text_file.name
        assert info['size'] > 0
        assert info['extension'] == '.txt'
        assert info['exists'] is True

    @pytest.mark.asyncio
    async def test_temporary_file_async_context_manager(self, file_handler: FileHandler):
        """Test async temporary file context manager."""
        mock_file = Mock(spec=UploadFile)
        content = b"async context test"
        mock_file.read = AsyncMock(side_effect=[content, b""])
        mock_file.seek = AsyncMock()

        filename = "async_context_test.txt"

        async with file_handler.temporary_file_async(mock_file, filename) as temp_path:
            # File should exist within context
            assert Path(temp_path).exists()
            assert Path(temp_path).read_bytes() == content

        # File should be cleaned up after context
        assert not Path(temp_path).exists()


class TestFileHandlerSecurityAndEdgeCases:
    """Test security and edge cases for FileHandler."""

    def test_sanitize_filename_security_comprehensive(self, file_handler: FileHandler, invalid_filename_samples: list):
        """Test comprehensive filename sanitization security."""
        for invalid_filename in invalid_filename_samples:
            sanitized = file_handler._sanitize_filename(invalid_filename)

            # Should never be empty
            assert len(sanitized) > 0

            # Should not contain dangerous characters
            dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
            for char in dangerous_chars:
                assert char not in sanitized

            # Should not be a Windows reserved name
            reserved_names = {'CON', 'PRN', 'AUX', 'NUL'}
            name_part = Path(sanitized).stem.upper()
            if name_part in reserved_names:
                assert sanitized.startswith('file_')

    def test_path_traversal_prevention(self, file_handler: FileHandler):
        """Test prevention of path traversal attacks."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32\\config",
        ]

        for dangerous_path in dangerous_paths:
            with pytest.raises(ValueError, match="Output directory outside allowed path"):
                file_handler.create_output_path("test.txt", dangerous_path)

    @patch('utils.file_handler.os.path.exists')
    @patch('utils.file_handler.os.remove')
    def test_cleanup_permission_error(self, mock_remove, mock_exists, file_handler: FileHandler):
        """Test cleanup handling of permission errors."""
        mock_exists.return_value = True
        mock_remove.side_effect = PermissionError("Permission denied")

        result = file_handler.cleanup_temp_file("some_file.txt")
        assert result is False

    @patch('utils.file_handler.Path.stat')
    def test_get_file_info_permission_error(self, mock_stat, file_handler: FileHandler):
        """Test file info handling of permission errors."""
        mock_stat.side_effect = PermissionError("Permission denied")

        info = file_handler.get_file_info("some_file.txt")
        assert 'error' in info
        assert info['exists'] is False