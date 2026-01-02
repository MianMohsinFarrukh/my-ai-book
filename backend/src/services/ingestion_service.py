"""
Content ingestion service to process Docusaurus markdown files
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import uuid4

from ..utils.chunking import chunk_markdown_document
from ..vector_db import get_vector_db_client
from ..models import ContentChunk
from ..database import get_db_session
from ..llm import get_llm_client
from .embedding_service import get_embedding_service


logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service for ingesting and processing book content
    """

    def __init__(self):
        self.vector_db = get_vector_db_client()
        self.llm_client = get_llm_client()
        self.embedding_service = get_embedding_service()

    async def ingest_document(self, file_path: str, source_path: str = "", metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Ingest a single document and store it in the vector database
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine source file path
            if source_path:
                source_file = source_path
            else:
                source_file = str(Path(file_path).relative_to(Path(file_path).parent))

            # Remove existing chunks for this source file to avoid duplicates
            async with get_db_session() as db_session:
                from sqlalchemy import delete
                stmt = delete(ContentChunk).where(ContentChunk.source_file == source_file)
                await db_session.execute(stmt)

                # Also delete from vector database
                await self.vector_db.delete_by_source(source_file)

                await db_session.commit()

            # Chunk the document
            chunks = chunk_markdown_document(
                markdown_content=content,
                chunk_size=1000,
                overlap=200,
                source_file=source_file
            )

            # Prepare data for storage
            texts = [chunk["content"] for chunk in chunks]
            chunk_metadata = []
            content_chunk_records = []

            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    "source_file": chunk["source_file"],
                    "chunk_index": chunk["index"],
                    "section": chunk.get("section", ""),
                    "hash": chunk["hash"]
                }
                chunk_metadata.append(chunk_meta)

                # Create ContentChunk record for the relational database
                content_chunk = ContentChunk(
                    source_file=chunk["source_file"],
                    chunk_index=chunk["index"],
                    content=chunk["content"],
                    embedding_id="",  # Will be set after embedding generation
                    metadata_=chunk_meta,
                    hash=chunk["hash"]
                )
                content_chunk_records.append(content_chunk)

            # Generate embeddings and store in vector database
            embedding_ids = await self.embedding_service.generate_and_store_embeddings(texts, chunk_metadata)

            # Update the content chunk records with embedding IDs and save to database
            async with get_db_session() as db_session:
                for i, record in enumerate(content_chunk_records):
                    record.embedding_id = embedding_ids[i]
                    db_session.add(record)
                await db_session.commit()

            logger.info(f"Successfully ingested {len(chunks)} chunks from {file_path}")
            return embedding_ids

        except Exception as e:
            logger.error(f"Error ingesting document {file_path}: {e}")
            raise

    async def ingest_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, List[str]]:
        """
        Ingest all markdown files in a directory
        """
        results = {}
        directory = Path(directory_path)

        # Find all markdown files
        if recursive:
            md_files = list(directory.rglob("*.md")) + list(directory.rglob("*.mdx"))
        else:
            md_files = list(directory.glob("*.md")) + list(directory.glob("*.mdx"))

        logger.info(f"Found {len(md_files)} markdown files to ingest")

        for md_file in md_files:
            try:
                file_results = await self.ingest_document(str(md_file))
                results[str(md_file)] = file_results
                logger.info(f"Successfully processed {md_file}")
            except Exception as e:
                logger.error(f"Failed to process {md_file}: {e}")
                results[str(md_file)] = []

        return results

    async def update_document(self, file_path: str, source_path: str = "") -> List[str]:
        """
        Update an existing document by deleting old chunks and ingesting new ones
        """
        # First, delete existing chunks for this source file from vector database
        await self.vector_db.delete_by_source(source_path or str(Path(file_path).relative_to(Path(file_path).parent)))

        # Remove old records from relational database
        async with get_db_session() as db_session:
            # This would require implementing a method to delete by source file
            # For now, we'll just ingest the new version
            pass

        # Ingest the new version
        return await self.ingest_document(file_path, source_path)

    async def get_ingestion_status(self) -> Dict[str, Any]:
        """
        Get the status of the ingestion process
        """
        collection_info = await self.vector_db.get_collection_info()

        async with get_db_session() as db_session:
            # This would require SQLAlchemy queries to get content chunk count
            # For now, just return vector database info
            pass

        return {
            "vector_db": collection_info,
            "status": "ready"
        }


# Global instance
_ingestion_service: Optional[IngestionService] = None


def get_ingestion_service() -> IngestionService:
    """
    Get the ingestion service instance
    """
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service