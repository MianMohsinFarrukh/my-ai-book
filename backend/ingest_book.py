#!/usr/bin/env python3
"""
Script to ingest book content into the RAG system
This script processes markdown files from your book and stores them in the vector database
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend/src to the Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.ingestion_service import get_ingestion_service
from src.database import init_db, DatabaseSettings
from src.vector_db import init_vector_db


async def main():
    """
    Main function to ingest book content
    """
    print("Initializing RAG system...")

    # Initialize database and vector database
    await init_db()
    await init_vector_db()

    # Get the ingestion service
    ingestion_service = get_ingestion_service()

    # Define the source directory for book content
    # By default, look for Docusaurus docs in the frontend directory
    book_content_dir = Path(__file__).parent / ".." / "frontend" / "docs"

    if not book_content_dir.exists():
        print(f"Book content directory not found: {book_content_dir}")
        print("Please make sure your book content is in the frontend/docs directory")
        return 1

    print(f"Ingesting book content from: {book_content_dir}")

    try:
        # Ingest all markdown files from the book content directory
        results = await ingestion_service.ingest_directory(str(book_content_dir))

        # Print results
        print(f"\nIngestion completed! Processed {len(results)} files:")
        for file_path, embedding_ids in results.items():
            if embedding_ids:
                print(f"  - {file_path}: {len(embedding_ids)} chunks")
            else:
                print(f"  - {file_path}: FAILED")

        # Get statistics
        stats = await ingestion_service.get_ingestion_status()
        print(f"\nSystem stats: {stats}")

        print("\nBook content has been successfully ingested into the RAG system!")
        print("You can now ask questions about your book content using the chatbot.")

        return 0

    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)