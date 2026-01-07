"""
Claude Code Subagents implementation
"""
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ..services.ingestion_service import get_ingestion_service
from ..services.rag_service import get_rag_service
from ..services.embedding_service import get_embedding_service
from .skills import get_retrieve_context_skill, get_answer_from_context_skill, get_validate_grounding_skill


logger = logging.getLogger(__name__)


class SubAgent(ABC):
    """
    Abstract base class for subagents
    """

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """
        Process the input and return the result
        """
        pass


class IngestionSubAgent(SubAgent):
    """
    Subagent for handling markdown ingestion and embedding
    """

    def __init__(self):
        self.ingestion_service = get_ingestion_service()

    async def process(self, source_path: str, chunk_size: int = 1000, overlap: int = 200) -> Dict[str, Any]:
        """
        Process markdown files and create embeddings

        Args:
            source_path: Path to the markdown files to process
            chunk_size: Size of text chunks (default: 1000)
            overlap: Overlap between chunks (default: 200)

        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Starting ingestion process for: {source_path}")

            # Use the ingestion service to process the directory
            results = await self.ingestion_service.ingest_directory(
                directory_path=source_path,
                recursive=True
            )

            total_files = len(results)
            total_chunks = sum(len(ids) for ids in results.values())

            logger.info(f"Ingestion completed: {total_files} files, {total_chunks} chunks")

            return {
                "status": "success",
                "files_processed": total_files,
                "chunks_created": total_chunks,
                "details": results
            }

        except Exception as e:
            logger.error(f"Error in ingestion subagent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "files_processed": 0,
                "chunks_created": 0,
                "details": {}
            }


class RetrievalSubAgent(SubAgent):
    """
    Subagent for performing vector search in Qdrant
    """

    def __init__(self):
        self.rag_service = get_rag_service()
        self.retrieve_context_skill = get_retrieve_context_skill()

    async def process(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector search and return relevant results

        Args:
            query: The search query
            top_k: Number of results to return (default: 5)

        Returns:
            List of relevant context items
        """
        try:
            logger.info(f"Starting retrieval process for query: {query[:50]}...")

            # Use the retrieve context skill
            context = await self.retrieve_context_skill.execute(query, top_k)

            logger.info(f"Retrieved {len(context)} items for query")

            return context

        except Exception as e:
            logger.error(f"Error in retrieval subagent: {e}")
            return []


class ResponseGuardSubAgent(SubAgent):
    """
    Subagent for ensuring answers are strictly grounded
    """

    def __init__(self):
        self.validate_grounding_skill = get_validate_grounding_skill()
        self.answer_from_context_skill = get_answer_from_context_skill()

    async def process(self, query: str, context: List[Dict[str, Any]],
                     response: str, min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Validate that the response is grounded in the provided context

        Args:
            query: The original query
            context: The context used for generating the response
            response: The generated response to validate
            min_confidence: Minimum grounding confidence threshold (default: 0.3)

        Returns:
            Dictionary with validation results and possibly corrected response
        """
        try:
            logger.info(f"Validating grounding for response to query: {query[:50]}...")

            # Validate grounding
            confidence = await self.validate_grounding_skill.execute(response, context)

            # Check if confidence is above threshold
            is_valid = confidence >= min_confidence

            # Prepare result
            result = {
                "original_response": response,
                "grounding_confidence": confidence,
                "is_valid": is_valid,
                "context_used": context
            }

            if not is_valid:
                logger.warning(f"Response has low grounding confidence ({confidence} < {min_confidence})")

                # Generate a more conservative response if confidence is low
                conservative_response = (
                    "I found some information related to your query, but I'm not completely confident "
                    "in my answer. The information I found is: " +
                    " ".join([item.get("content", "")[:200] for item in context[:2]])
                )

                result["corrected_response"] = conservative_response
                result["final_response"] = conservative_response
            else:
                result["final_response"] = response

            logger.info(f"Grounding validation completed with confidence: {confidence}")

            return result

        except Exception as e:
            logger.error(f"Error in response guard subagent: {e}")

            return {
                "original_response": response,
                "grounding_confidence": 0.0,
                "is_valid": False,
                "final_response": "I couldn't validate this response properly. Please ask your question again.",
                "error": str(e)
            }


# Global instances for the subagents
_ingestion_subagent: Optional[IngestionSubAgent] = None
_retrieval_subagent: Optional[RetrievalSubAgent] = None
_response_guard_subagent: Optional[ResponseGuardSubAgent] = None


def get_ingestion_subagent() -> IngestionSubAgent:
    """
    Get the ingestion subagent instance
    """
    global _ingestion_subagent
    if _ingestion_subagent is None:
        _ingestion_subagent = IngestionSubAgent()
    return _ingestion_subagent


def get_retrieval_subagent() -> RetrievalSubAgent:
    """
    Get the retrieval subagent instance
    """
    global _retrieval_subagent
    if _retrieval_subagent is None:
        _retrieval_subagent = RetrievalSubAgent()
    return _retrieval_subagent


def get_response_guard_subagent() -> ResponseGuardSubAgent:
    """
    Get the response guard subagent instance
    """
    global _response_guard_subagent
    if _response_guard_subagent is None:
        _response_guard_subagent = ResponseGuardSubAgent()
    return _response_guard_subagent


def get_all_subagents() -> Dict[str, SubAgent]:
    """
    Get all available subagents
    """
    return {
        "ingestion_subagent": get_ingestion_subagent(),
        "retrieval_subagent": get_retrieval_subagent(),
        "response_guard_subagent": get_response_guard_subagent()
    }