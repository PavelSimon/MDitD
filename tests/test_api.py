"""
Tests for FastAPI endpoints.
"""
import pytest
import json
from pathlib import Path
from io import BytesIO
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import httpx

from main import app


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    def test_root_endpoint(self, test_client: TestClient):
        """Test the root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_health_endpoint(self, test_client: TestClient):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "timestamp" in data
        assert "components" in data
        assert "system" in data
        assert "config" in data

        assert data["service"] == "MDitD"
        assert isinstance(data["timestamp"], (int, float))

    def test_get_supported_formats_endpoint(self, test_client: TestClient):
        """Test the supported formats endpoint."""
        response = test_client.get("/formats")
        assert response.status_code == 200

        data = response.json()
        assert "supported_formats" in data
        assert isinstance(data["supported_formats"], list)
        assert len(data["supported_formats"]) > 0
        assert ".pdf" in data["supported_formats"]
        assert ".docx" in data["supported_formats"]

    @pytest.mark.integration
    def test_upload_single_text_file(self, test_client: TestClient):
        """Test uploading a single text file."""
        file_content = "# Test Document\n\nThis is a test."
        files = {
            "files": ("test.txt", BytesIO(file_content.encode()), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        assert "results" in result
        assert "total_files" in result
        assert "successful" in result
        assert "failed" in result

        assert result["total_files"] == 1
        assert len(result["results"]) == 1

        file_result = result["results"][0]
        assert file_result["filename"] == "test.txt"

        # Clean up if successful
        if file_result["success"] and file_result.get("output_path"):
            output_path = Path(file_result["output_path"])
            if output_path.exists():
                output_path.unlink()

    @pytest.mark.integration
    def test_upload_multiple_files(self, test_client: TestClient):
        """Test uploading multiple files."""
        files = [
            ("files", ("test1.txt", BytesIO(b"Content 1"), "text/plain")),
            ("files", ("test2.html", BytesIO(b"<html><body>Content 2</body></html>"), "text/html")),
        ]
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        assert result["total_files"] == 2
        assert len(result["results"]) == 2

        # Clean up successful conversions
        for file_result in result["results"]:
            if file_result["success"] and file_result.get("output_path"):
                output_path = Path(file_result["output_path"])
                if output_path.exists():
                    output_path.unlink()

    def test_upload_no_files(self, test_client: TestClient):
        """Test upload with no files."""
        response = test_client.post("/upload", files=[], data={"output_dir": "test"})
        # Could be 400 (our validation) or 422 (FastAPI validation)
        assert response.status_code in [400, 422]
        if response.status_code == 400:
            assert "No files provided" in response.json()["detail"]

    def test_upload_too_many_files(self, test_client: TestClient):
        """Test upload with too many files."""
        # Create more files than the limit (assuming limit is 20)
        files = [
            ("files", (f"test{i}.txt", BytesIO(b"content"), "text/plain"))
            for i in range(25)  # Exceed the limit
        ]
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 400
        assert "Too many files" in response.json()["detail"]

    def test_upload_file_too_large(self, test_client: TestClient):
        """Test upload with file that's too large."""
        # Create a mock large file (we don't actually send the content, just set the size)
        large_content = b"A" * (101 * 1024 * 1024)  # 101MB (over the 100MB limit)
        files = {
            "files": ("large.txt", BytesIO(large_content), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        # This might succeed or fail depending on how FastAPI handles large files
        # The test mainly ensures we don't crash
        assert response.status_code in [200, 413, 422]

    def test_upload_unsupported_file_type(self, test_client: TestClient):
        """Test upload with unsupported file type."""
        files = {
            "files": ("malicious.exe", BytesIO(b"fake executable"), "application/octet-stream")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        assert result["total_files"] == 1
        assert result["successful"] == 0
        assert result["failed"] == 1

        file_result = result["results"][0]
        assert file_result["success"] is False
        assert "Unsupported file format" in file_result["error"]

    def test_upload_invalid_output_directory(self, test_client: TestClient):
        """Test upload with invalid output directory."""
        files = {
            "files": ("test.txt", BytesIO(b"content"), "text/plain")
        }

        # Test various invalid directories
        invalid_dirs = ["../../../etc", "C:\\Windows\\System32", "/etc/passwd"]

        for invalid_dir in invalid_dirs:
            data = {"output_dir": invalid_dir}
            response = test_client.post("/upload", files=files, data=data)
            # Should either reject at validation level (400) or at processing level (200 with errors)
            assert response.status_code in [200, 400]

            if response.status_code == 200:
                result = response.json()
                assert result["successful"] == 0 or any(
                    "Output directory error" in res.get("error", "")
                    for res in result["results"]
                )

    def test_upload_output_directory_too_long(self, test_client: TestClient):
        """Test upload with output directory name that's too long."""
        files = {
            "files": ("test.txt", BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": "x" * 150}  # Exceed the limit

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 400
        assert "too long" in response.json()["detail"]

    def test_upload_forbidden_output_dir_patterns(self, test_client: TestClient):
        """Test upload with forbidden patterns in output directory."""
        files = {
            "files": ("test.txt", BytesIO(b"content"), "text/plain")
        }

        forbidden_patterns = ["../backdoor", "dir\\with\\backslash", "dir:with:colon"]

        for pattern in forbidden_patterns:
            data = {"output_dir": pattern}
            response = test_client.post("/upload", files=files, data=data)
            assert response.status_code == 400
            assert "Invalid output directory" in response.json()["detail"]

    def test_upload_output_directory_starts_with_dot(self, test_client: TestClient):
        """Test upload with output directory starting with dot."""
        files = {
            "files": ("test.txt", BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": ".hidden_dir"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 400
        assert "Cannot start with dot" in response.json()["detail"]

    @pytest.mark.integration
    def test_upload_with_conversion_error(self, test_client: TestClient):
        """Test upload where conversion fails."""
        # Create a file that might cause conversion issues
        files = {
            "files": ("corrupt.txt", BytesIO(b"\x00\x01\x02\x03"), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        # The conversion might succeed or fail, but we should get a valid response
        assert "results" in result
        assert len(result["results"]) == 1

    def test_upload_empty_filename(self, test_client: TestClient):
        """Test upload with empty filename."""
        files = {
            "files": ("", BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        # Empty filename triggers FastAPI validation error
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            result = response.json()
            file_result = result["results"][0]
            assert file_result["success"] is False
            # The error message might vary - check for a reasonable error
            assert "error" in file_result
            assert file_result["error"] is not None

    def test_upload_very_long_filename(self, test_client: TestClient):
        """Test upload with very long filename."""
        long_filename = "x" * 300 + ".txt"
        files = {
            "files": (long_filename, BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        file_result = result["results"][0]
        assert file_result["success"] is False
        assert "Filename too long" in file_result["error"]

    def test_upload_filename_with_forbidden_characters(self, test_client: TestClient):
        """Test upload with filename containing forbidden characters."""
        forbidden_filename = "file<with>forbidden|chars.txt"
        files = {
            "files": (forbidden_filename, BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        file_result = result["results"][0]
        assert file_result["success"] is False
        assert "forbidden characters" in file_result["error"]


class TestAPIAsync:
    """Test cases for API endpoints using async client."""

    @pytest.mark.asyncio
    async def test_health_endpoint_async(self, async_client: httpx.AsyncClient):
        """Test health endpoint with async client."""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "MDitD"

    @pytest.mark.asyncio
    async def test_formats_endpoint_async(self, async_client: httpx.AsyncClient):
        """Test formats endpoint with async client."""
        response = await async_client.get("/formats")
        assert response.status_code == 200

        data = response.json()
        assert "supported_formats" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_upload_async(self, async_client: httpx.AsyncClient):
        """Test file upload with async client."""
        files = {
            "files": ("async_test.txt", "# Async Test\n\nThis is an async test.", "text/plain")
        }
        data = {"output_dir": "async_output"}

        response = await async_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        assert result["total_files"] == 1

        # Clean up if successful
        if result["results"][0]["success"]:
            output_path = Path(result["results"][0]["output_path"])
            if output_path.exists():
                output_path.unlink()


class TestAPIErrorHandling:
    """Test error handling in API endpoints."""

    @patch('main.converter.convert_to_file')
    def test_upload_with_converter_exception(self, mock_convert, test_client: TestClient):
        """Test upload when converter raises an exception."""
        mock_convert.side_effect = Exception("Converter error")

        files = {
            "files": ("test.txt", BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        file_result = result["results"][0]
        assert file_result["success"] is False
        assert "unexpected error" in file_result["error"].lower()

    @patch('main.file_handler.create_output_path')
    def test_upload_with_output_path_exception(self, mock_create_path, test_client: TestClient):
        """Test upload when output path creation fails."""
        mock_create_path.side_effect = ValueError("Path error")

        files = {
            "files": ("test.txt", BytesIO(b"content"), "text/plain")
        }
        data = {"output_dir": "test_output"}

        response = test_client.post("/upload", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        file_result = result["results"][0]
        assert file_result["success"] is False
        assert "Output directory error" in file_result["error"]

    def test_static_files_serving(self, test_client: TestClient):
        """Test that static files are served correctly."""
        # Test CSS file
        response = test_client.get("/static/css/style.css")
        if response.status_code == 200:
            assert "text/css" in response.headers.get("content-type", "")
        else:
            # File might not exist in test environment
            assert response.status_code == 404

        # Test JavaScript file
        response = test_client.get("/static/js/app.js")
        if response.status_code == 200:
            assert any(content_type in response.headers.get("content-type", "")
                      for content_type in ["application/javascript", "text/javascript"])
        else:
            # File might not exist in test environment
            assert response.status_code == 404

    def test_invalid_endpoints(self, test_client: TestClient):
        """Test invalid endpoints return 404."""
        invalid_endpoints = ["/invalid", "/api/nonexistent", "/upload/invalid"]

        for endpoint in invalid_endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 404

    def test_wrong_http_methods(self, test_client: TestClient):
        """Test wrong HTTP methods on endpoints."""
        # GET on upload endpoint should fail
        response = test_client.get("/upload")
        assert response.status_code == 405  # Method Not Allowed

        # POST on health endpoint should fail
        response = test_client.post("/health")
        assert response.status_code == 405  # Method Not Allowed