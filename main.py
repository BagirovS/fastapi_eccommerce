"""
Entry-point module for Uvicorn when running from the project root.

This project keeps the FastAPI app in `app/main.py`, but many commands/tools
expect `main:app` by default. Re-export the ASGI app here to make:

    uvicorn main:app --reload

work from the repository root.
"""

from app.main import app  # noqa: F401

