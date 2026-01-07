"""
RAG (Retrieval Augmented Generation) query service
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from ..vector_db import get_vector_db_client
from ..llm import get_llm_client
from ..models import ChatSession, ChatMessage
from ..database import get_db_session
from .embedding_service import get_embedding_service


logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for performing RAG queries - retrieving relevant content and generating responses
    """

    def __init__(self):
        self.vector_db = get_vector_db_client()
        self.llm_client = get_llm_client()
        self.embedding_service = get_embedding_service()

    async def retrieve_context(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector database based on the query
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_query_embedding(query)

            # Search for similar content in the vector database
            results = await self.vector_db.search_similar(
                query_vector=query_embedding,
                limit=top_k,
                filters=filters
            )

            return results

        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}")
            return []

    async def search_content(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for content without generating a response
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_query_embedding(query)

            # Search for similar content in the vector database
            results = await self.vector_db.search_similar(
                query_vector=query_embedding,
                limit=top_k,
                filters=filters
            )

            return results

        except Exception as e:
            logger.error(f"Error searching content for query '{query}': {e}")
            return []

    async def get_all_sources(self) -> List[str]:
        """
        Get all content sources that have been ingested
        This would typically require querying the vector database or relational database
        For now, we'll return a placeholder implementation
        """
        try:
            # This would require a more sophisticated implementation
            # For now, we'll return an empty list or implement a proper source query
            # In a real implementation, you'd query the database for unique source files
            from ..database import get_db_session
            from ..models import ContentChunk
            from sqlalchemy import select, distinct

            async with get_db_session() as db_session:
                result = await db_session.execute(
                    select(distinct(ContentChunk.source_file))
                )
                sources = [row[0] for row in result]

            return sources

        except Exception as e:
            logger.error(f"Error retrieving sources: {e}")
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system
        """
        try:
            # Get vector database collection info
            collection_info = await self.vector_db.get_collection_info()

            # Get content chunk count from relational database
            from ..database import get_db_session
            from ..models import ContentChunk
            from sqlalchemy import func, select

            async with get_db_session() as db_session:
                chunk_count = await db_session.execute(
                    select(func.count(ContentChunk.id))
                )
                chunk_count = chunk_count.scalar()

            # Combine stats
            stats = {
                "vector_db": collection_info,
                "content_chunks_count": chunk_count,
                "embedding_service": "OpenAI",
                "llm_service": "OpenAI",
                "total_sources": len(await self.get_all_sources())
            }

            return stats

        except Exception as e:
            logger.error(f"Error retrieving stats: {e}")
            return {"error": str(e)}

    async def answer_from_context(self, query: str, context: List[Dict[str, Any]], system_prompt: Optional[str] = None) -> str:
        """
        Generate an answer based on the provided context
        """
        try:
            # Format the context for the LLM
            context_text = "\n\n".join([item["content"] for item in context])

            if not context_text.strip():
                return "I couldn't find any relevant information in the book to answer your question."

            # Create a detailed prompt for the LLM
            if system_prompt is None:
                system_prompt = (
                    "You are an AI assistant that answers questions based strictly on the provided book content. "
                    "Only use information from the context provided below to answer the user's question. "
                    "If the context doesn't contain enough information to answer the question, say so clearly. "
                    "Do not make up information or hallucinate beyond what's in the provided context. "
                    "Always cite the source of information when possible."
                )

            full_prompt = (
                f"Context:\n{context_text}\n\n"
                f"Question: {query}\n\n"
                f"Please provide a detailed answer based only on the context above. "
                f"If the context doesn't contain the information needed to answer, say so clearly."
            )

            # Generate response using the LLM
            response = await self.llm_client.generate_response(full_prompt, system_prompt)

            return response

        except Exception as e:
            logger.error(f"Error generating response for query '{query}': {e}")
            return "Sorry, I encountered an error while processing your question."

    async def validate_grounding(self, response: str, context: List[Dict[str, Any]]) -> float:
        """
        Validate that the response is grounded in the provided context
        This is a basic implementation - in practice, you might use more sophisticated validation
        """
        try:
            # Simple validation: check if key terms from context appear in response
            context_text = " ".join([item["content"] for item in context]).lower()
            response_lower = response.lower()

            # Count how many context terms appear in the response
            context_words = set(context_text.split()[:50])  # Use first 50 words as representative
            response_words = set(response_lower.split())

            if not context_words:
                return 0.0

            overlap = len(context_words.intersection(response_words))
            grounding_score = overlap / len(context_words)

            # Ensure score is between 0 and 1
            return min(1.0, grounding_score)

        except Exception as e:
            logger.error(f"Error validating grounding for response: {e}")
            return 0.0

    async def query(self, query: str, top_k: int = 5, validate_grounding: bool = True, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a complete RAG query - retrieve context and generate response
        """
        # Retrieve relevant context
        context = await self.retrieve_context(query, top_k, filters)

        # Generate response from context
        response = await self.answer_from_context(query, context)

        result = {
            "response": response,
            "context_used": context,
            "grounding_confidence": 0.0  # Default value
        }

        # Validate grounding if requested
        if validate_grounding and context:
            grounding_score = await self.validate_grounding(response, context)
            result["grounding_confidence"] = grounding_score

        return result

    async def query_with_selected_text(self, query: str, selected_text: str, top_k: int = 5, validate_grounding: bool = True) -> Dict[str, Any]:
        """
        Perform a query using user-selected text as the primary context
        This bypasses the vector search and uses the provided text directly
        """
        # Format the selected text as context
        context = [{
            "id": str(uuid4()),
            "content": selected_text,
            "metadata": {"source": "user_selected_text"},
            "similarity": 1.0  # Highest similarity since this is the provided context
        }]

        # Generate response from the selected context
        response = await self.answer_from_context(query, context)

        result = {
            "response": response,
            "context_used": context,
            "grounding_confidence": 0.0  # Default value
        }

        # Validate grounding if requested
        if validate_grounding and context:
            grounding_score = await self.validate_grounding(response, context)
            result["grounding_confidence"] = grounding_score

        return result


# Global instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get the RAG service instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service