"""
Script to run the Book RAG Chatbot server
"""
import uvicorn
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.main import app


def run_server():
    """
    Run the FastAPI server
    """
    print("Starting Book RAG Chatbot server...")
    print("API documentation available at: http://localhost:8000/docs")

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    run_server()