"""
Pytest configuration and shared fixtures for MDitD tests.
"""
import pytest
import pytest_asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
import httpx
import asyncio

from main import app
from utils.converter import DocumentConverter
from utils.file_handler import FileHandler
from settings import settings


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with httpx.AsyncClient(base_url="http://test") as client:
        # httpx syntax changed - use transport directly
        from httpx import ASGITransport
        client._transport = ASGITransport(app=app)
        yield client


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_uploads_dir(temp_dir: Path) -> Path:
    """Create a temporary uploads directory."""
    uploads_dir = temp_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    return uploads_dir


@pytest.fixture
def test_output_dir(temp_dir: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def document_converter() -> DocumentConverter:
    """Create a DocumentConverter instance for testing."""
    return DocumentConverter()


@pytest.fixture
def file_handler(test_uploads_dir: Path, test_output_dir: Path) -> FileHandler:
    """Create a FileHandler instance with test directories."""
    return FileHandler(uploads_dir=str(test_uploads_dir), output_dir=str(test_output_dir))


@pytest.fixture
def sample_text_file(temp_dir: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("# Sample Document\n\nThis is a test document.", encoding="utf-8")
    return file_path


@pytest.fixture
def sample_html_file(temp_dir: Path) -> Path:
    """Create a sample HTML file for testing."""
    file_path = temp_dir / "sample.html"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Document</title></head>
    <body>
        <h1>Sample Document</h1>
        <p>This is a test HTML document.</p>
    </body>
    </html>
    """
    file_path.write_text(html_content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_json_file(temp_dir: Path) -> Path:
    """Create a sample JSON file for testing."""
    file_path = temp_dir / "sample.json"
    json_content = '{"title": "Sample Document", "content": "This is a test JSON document."}'
    file_path.write_text(json_content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_large_file(temp_dir: Path) -> Path:
    """Create a large file for testing size limits."""
    file_path = temp_dir / "large.txt"
    # Create a 1MB file
    content = "A" * (1024 * 1024)
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_binary_file(temp_dir: Path) -> Path:
    """Create a sample binary file for testing."""
    file_path = temp_dir / "sample.bin"
    # Create a small binary file
    file_path.write_bytes(b"\x00\x01\x02\x03\x04\x05")
    return file_path


@pytest.fixture
def invalid_filename_samples() -> list[str]:
    """Provide a list of invalid filenames for testing."""
    return [
        "../../../etc/passwd",  # Path traversal
        "con.txt",  # Reserved Windows name
        "file with spaces and special chars <>.txt",
        "very_long_filename_" + "x" * 300 + ".txt",  # Too long
        "file\x00with\x01null.txt",  # Control characters
        "",  # Empty filename
        "...",  # Just dots
        "file|with|pipes.txt",  # Pipe characters
        "file\"with\"quotes.txt",  # Quotes
    ]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings to default values before each test."""
    # This ensures tests don't interfere with each other
    yield
    # Any cleanup logic here if needed