# Gemini Project: MDitD - Markdown Conversion Web App

## Project Overview

This project is a Python-based web application named "MDitD" that converts various document formats to Markdown. It's built using the FastAPI framework for the web server and the `markitdown` library for the core conversion functionality. The application provides a simple web interface where users can upload one or more files, which are then processed concurrently and converted to Markdown format.

The application is designed with a clear separation of concerns:
- **`main.py`**: The main FastAPI application, handling routing, request/response logic, and concurrent file processing.
- **`utils/converter.py`**: A `DocumentConverter` class that wraps the `markitdown` library, managing file format support and the conversion process.
- **`utils/file_handler.py`**: A `FileHandler` class responsible for all file system operations, including saving uploads, sanitizing filenames, and managing output directories.
- **`templates/` and `static/`**: Standard directories for web assets, containing HTML templates and CSS/JavaScript files for the frontend.
- **`settings.py`**: For application configuration.
- **`logging_config.py`**: For configuring logging.

## Building and Running

The project uses `uv` for dependency management and running the application.

**1. Install Dependencies:**
```bash
uv sync
```

**2. Run the Application:**
There are two ways to run the application:

*   **Using the main script:**
    ```bash
    uv run python main.py
    ```

*   **Using uvicorn for development (with auto-reload):**
    ```bash
    uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ```

The application will be available at **http://localhost:8001**.

**3. Running Tests:**
The project includes tests using `pytest`. To run the tests, execute the following command:
```bash
pytest
```

## Development Conventions

*   **Framework:** The project uses [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Dependency Management:** Project dependencies are managed with `uv` and are listed in the `pyproject.toml` file.
*   **Testing:** The project uses `pytest` for unit and integration testing. Tests are located in the `tests/` directory.
*   **Asynchronous Operations:** The application leverages Python's `asyncio` for non-blocking I/O operations, particularly for handling file uploads and processing, to ensure high performance and concurrency.
*   **Configuration:** Application settings are managed in the `settings.py` file, which uses `pydantic-settings` for robust configuration management.
*   **Logging:** The application uses Python's built-in `logging` module, configured in `logging_config.py`.
*   **Code Style:** The code follows standard Python conventions (PEP 8).
