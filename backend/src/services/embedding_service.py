"""
Embedding generation service
"""
import logging
import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..database import get_db_session
from ..models import ContentChunk
from ..llm import get_llm_client


logger = logging.getLogger(__name__)


class EmbeddingSettings(BaseSettings):
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-ada-002"

    class Config:
        env_file = ".env"
        env_prefix = "OPENAI_"
        extra = "ignore"  # Ignore extra environment variables


class EmbeddingService:
    """
    Service for generating and managing embeddings
    """

    def __init__(self, settings: EmbeddingSettings = None):
        self.settings = settings or EmbeddingSettings()
        # For embeddings, we specifically use OpenAI API since OpenRouter typically doesn't provide embedding endpoints
        # Try to get the API key from settings first, then from environment directly as fallback
        api_key = self.settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OpenAI API key not found. Embedding functionality will not work.")

        # Initialize OpenAI client for embeddings
        self.client = AsyncOpenAI(api_key=api_key)

        self.llm_client = get_llm_client()

    async def generate_embeddings(self, texts: List[str], method: str = "openai") -> List[List[float]]:
        """
        Generate embeddings for a list of texts using specified method
        """
        if not texts:
            return []

        if method == "openai":
            return await self._generate_openai_embeddings(texts)
        elif method == "claude":
            return await self._generate_claude_embeddings(texts)
        else:
            # Default to OpenAI
            return await self._generate_openai_embeddings(texts)

    async def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API
        """
        try:
            # Call OpenAI embeddings API
            response = await self.client.embeddings.create(
                input=texts,
                model=self.settings.embedding_model
            )

            # Extract embeddings from response
            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)

            return embeddings

        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            raise

    async def _generate_claude_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Claude's capabilities (simulated approach)
        In a real implementation, this would use Anthropic's embedding API when available
        or use Claude to generate semantic representations
        """
        logger.warning("Claude embedding generation is simulated. Using OpenAI as fallback.")
        return await self._generate_openai_embeddings(texts)

    async def generate_hybrid_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate hybrid embeddings combining multiple approaches
        """
        # For now, just return OpenAI embeddings
        # In a real implementation, this would combine embeddings from multiple sources
        return await self._generate_openai_embeddings(texts)

    async def generate_semantic_summary(self, texts: List[str]) -> List[str]:
        """
        Generate semantic summaries using LLMs that can be used as additional context
        """
        summaries = []

        for text in texts:
            # Use the LLM client to generate a semantic summary
            try:
                # Using the main LLM client (OpenRouter/OpenAI)
                summary_prompt = f"Summarize the key concepts in: {text[:2000]}"
                summary = await self.llm_client.generate_response(summary_prompt)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Error generating semantic summary: {e}")
                # Fallback to original text if summary generation fails
                summaries.append(text[:500])  # Use first 500 chars as fallback

        return summaries

    async def generate_and_store_embeddings(
        self,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        method: str = "openai",
        generate_summaries: bool = False
    ) -> List[str]:
        """
        Generate embeddings and store them in the vector database

        Args:
            texts: List of texts to embed
            metadata: Metadata for each text
            method: Embedding generation method ('openai', 'claude', or 'hybrid')
            generate_summaries: Whether to also generate semantic summaries
        """
        # Generate embeddings
        embeddings = await self.generate_embeddings(texts, method=method)

        # Generate semantic summaries if requested
        summaries = []
        if generate_summaries:
            summaries = await self.generate_semantic_summary(texts)

        # This would integrate with the vector database
        # For now, return placeholder IDs
        from ..vector_db import get_vector_db_client
        vector_db = get_vector_db_client()

        # Generate random IDs for the embeddings
        import uuid
        embedding_ids = [str(uuid.uuid4()) for _ in embeddings]

        # Prepare metadata with additional information if summaries are available
        extended_metadata = []
        for i, meta in enumerate(metadata):
            extended_meta = meta.copy()
            if generate_summaries and i < len(summaries):
                extended_meta["semantic_summary"] = summaries[i]
            extended_metadata.append(extended_meta)

        # Store in vector database with actual embeddings
        await vector_db.add_embeddings(texts, embeddings, extended_metadata, embedding_ids)

        # Update the ContentChunk records with embedding IDs
        async with get_db_session() as db_session:
            for i, meta in enumerate(metadata):
                # Find the content chunk by source and index
                from sqlalchemy import select
                result = await db_session.execute(
                    select(ContentChunk).where(
                        (ContentChunk.source_file == meta["source_file"]) &
                        (ContentChunk.chunk_index == meta["chunk_index"])
                    )
                )
                chunk = result.scalar()

                if chunk:
                    # Update the embedding_id
                    chunk.embedding_id = embedding_ids[i]
                    if generate_summaries and i < len(summaries):
                        if chunk.metadata_ is None:
                            chunk.metadata_ = {}
                        chunk.metadata_["semantic_summary"] = summaries[i]

            await db_session.commit()

        return embedding_ids

    async def generate_query_embedding(self, query: str, method: str = "openai") -> List[float]:
        """
        Generate embedding for a query
        """
        embeddings = await self.generate_embeddings([query], method=method)
        return embeddings[0] if embeddings else []

    async def batch_process_embeddings(
        self,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        batch_size: int = 10,
        method: str = "openai"
    ) -> List[str]:
        """
        Process embeddings in batches to handle large datasets efficiently
        """
        all_embedding_ids = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]

            batch_embedding_ids = await self.generate_and_store_embeddings(
                batch_texts, batch_metadata, method=method
            )
            all_embedding_ids.extend(batch_embedding_ids)

        return all_embedding_ids

    async def update_embeddings_for_file(
        self,
        source_file: str,
        texts: List[str],
        chunk_indices: List[int],
        method: str = "openai"
    ) -> List[str]:
        """
        Update embeddings for a specific file, replacing existing ones
        """
        from ..vector_db import get_vector_db_client
        vector_db = get_vector_db_client()

        # Delete existing embeddings for this file
        await vector_db.delete_by_source(source_file)

        # Prepare metadata for new chunks
        metadata = []
        for idx, chunk_idx in enumerate(chunk_indices):
            metadata.append({
                "source_file": source_file,
                "chunk_index": chunk_idx,
                "original_index": idx
            })

        # Generate and store new embeddings
        embedding_ids = await self.generate_and_store_embeddings(
            texts, metadata, method=method, generate_summaries=True
        )

        return embedding_ids


# Global instance
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the embedding service instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service