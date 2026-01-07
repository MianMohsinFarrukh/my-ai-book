"""
OpenAI Agent SDK Skills for RAG Chatbot
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from src.services.rag_service import get_rag_service
from src.vector_db import get_vector_db_client
from src.services.embedding_service import get_embedding_service

load_dotenv()

logger = logging.getLogger(__name__)

class RetrieveContextSkill:
    """
    Skill to retrieve relevant context from the vector database for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for the given query

        Args:
            query: The query to search for
            top_k: Number of results to return (default: 5)

        Returns:
            List of context items with source, content, and similarity
        """
        try:
            context = await self.rag_service.retrieve_context(query, top_k)
            logger.info(f"Retrieved {len(context)} context items for query: {query[:50]}...")

            # Format context for agent consumption
            formatted_context = []
            for item in context:
                formatted_item = {
                    "id": item.get("id", ""),
                    "content": item.get("content", ""),
                    "source": item.get("metadata", {}).get("source", ""),
                    "similarity": item.get("similarity", 0.0)
                }
                formatted_context.append(formatted_item)

            return formatted_context
        except Exception as e:
            logger.error(f"Error in retrieve_context skill: {e}")
            return []


class SearchContentSkill:
    """
    Skill to search for content without generating a response for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for content without generating a response

        Args:
            query: The query to search for
            top_k: Number of results to return (default: 10)

        Returns:
            List of content items with source and content
        """
        try:
            results = await self.rag_service.search_content(query, top_k)
            logger.info(f"Found {len(results)} content items for query: {query[:50]}...")

            # Format results for agent consumption
            formatted_results = []
            for item in results:
                formatted_item = {
                    "id": item.get("id", ""),
                    "content": item.get("content", ""),
                    "source": item.get("metadata", {}).get("source", ""),
                    "similarity": item.get("similarity", 0.0)
                }
                formatted_results.append(formatted_item)

            return formatted_results
        except Exception as e:
            logger.error(f"Error in search_content skill: {e}")
            return []


class AnswerFromContextSkill:
    """
    Skill to generate answers based on provided context for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self, query: str, context: List[Dict[str, Any]],
                     system_prompt: Optional[str] = None) -> str:
        """
        Generate an answer based on the provided context

        Args:
            query: The original query
            context: List of context items to use for answering
            system_prompt: Optional system prompt to guide the response

        Returns:
            Generated answer string
        """
        try:
            answer = await self.rag_service.answer_from_context(query, context, system_prompt)
            logger.info(f"Generated answer for query: {query[:50]}...")
            return answer
        except Exception as e:
            logger.error(f"Error in answer_from_context skill: {e}")
            return "Sorry, I encountered an error while generating an answer."


class ValidateGroundingSkill:
    """
    Skill to validate that responses are grounded in provided context for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self, response: str, context: List[Dict[str, Any]]) -> float:
        """
        Validate that the response is grounded in the provided context

        Args:
            response: The response to validate
            context: The context that should ground the response

        Returns:
            Grounding confidence score (0.0 to 1.0)
        """
        try:
            confidence = await self.rag_service.validate_grounding(response, context)
            logger.info(f"Calculated grounding confidence: {confidence}")
            return confidence
        except Exception as e:
            logger.error(f"Error in validate_grounding skill: {e}")
            return 0.0


class GetRAGStatsSkill:
    """
    Skill to get statistics about the RAG system for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system

        Returns:
            Dictionary with RAG system statistics
        """
        try:
            stats = await self.rag_service.get_stats()
            logger.info("Retrieved RAG system statistics")
            return stats
        except Exception as e:
            logger.error(f"Error in get_rag_stats skill: {e}")
            return {"error": str(e)}


class QueryRAGSkill:
    """
    Skill to perform a complete RAG query for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self, query: str, top_k: int = 5, validate_grounding: bool = True) -> Dict[str, Any]:
        """
        Perform a complete RAG query - retrieve context and generate response

        Args:
            query: The query to process
            top_k: Number of results to retrieve (default: 5)
            validate_grounding: Whether to validate grounding (default: True)

        Returns:
            Dictionary with response, context used, and grounding confidence
        """
        try:
            result = await self.rag_service.query(query, top_k, validate_grounding)
            logger.info(f"Completed RAG query for: {query[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error in query_rag skill: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your query.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "error": str(e)
            }


class QueryWithSelectedTextSkill:
    """
    Skill to perform a query using selected text as primary context for OpenAI Agent SDK
    """

    def __init__(self):
        self.rag_service = get_rag_service()

    async def execute(self, query: str, selected_text: str, top_k: int = 5, validate_grounding: bool = True) -> Dict[str, Any]:
        """
        Perform a query using user-selected text as the primary context

        Args:
            query: The query to process
            selected_text: The selected text to use as primary context
            top_k: Number of additional results to retrieve (default: 5)
            validate_grounding: Whether to validate grounding (default: True)

        Returns:
            Dictionary with response, context used, and grounding confidence
        """
        try:
            result = await self.rag_service.query_with_selected_text(query, selected_text, top_k, validate_grounding)
            logger.info(f"Completed query with selected text for: {query[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error in query_with_selected_text skill: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your query.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "error": str(e)
            }


# Global instances for the skills
_retrieve_context_skill: Optional[RetrieveContextSkill] = None
_search_content_skill: Optional[SearchContentSkill] = None
_answer_from_context_skill: Optional[AnswerFromContextSkill] = None
_validate_grounding_skill: Optional[ValidateGroundingSkill] = None
_get_rag_stats_skill: Optional[GetRAGStatsSkill] = None
_query_rag_skill: Optional[QueryRAGSkill] = None
_query_with_selected_text_skill: Optional[QueryWithSelectedTextSkill] = None


def get_retrieve_context_skill() -> RetrieveContextSkill:
    """
    Get the retrieve context skill instance
    """
    global _retrieve_context_skill
    if _retrieve_context_skill is None:
        _retrieve_context_skill = RetrieveContextSkill()
    return _retrieve_context_skill


def get_search_content_skill() -> SearchContentSkill:
    """
    Get the search content skill instance
    """
    global _search_content_skill
    if _search_content_skill is None:
        _search_content_skill = SearchContentSkill()
    return _search_content_skill


def get_answer_from_context_skill() -> AnswerFromContextSkill:
    """
    Get the answer from context skill instance
    """
    global _answer_from_context_skill
    if _answer_from_context_skill is None:
        _answer_from_context_skill = AnswerFromContextSkill()
    return _answer_from_context_skill


def get_validate_grounding_skill() -> ValidateGroundingSkill:
    """
    Get the validate grounding skill instance
    """
    global _validate_grounding_skill
    if _validate_grounding_skill is None:
        _validate_grounding_skill = ValidateGroundingSkill()
    return _validate_grounding_skill


def get_rag_stats_skill() -> GetRAGStatsSkill:
    """
    Get the RAG stats skill instance
    """
    global _get_rag_stats_skill
    if _get_rag_stats_skill is None:
        _get_rag_stats_skill = GetRAGStatsSkill()
    return _get_rag_stats_skill


def get_query_rag_skill() -> QueryRAGSkill:
    """
    Get the query RAG skill instance
    """
    global _query_rag_skill
    if _query_rag_skill is None:
        _query_rag_skill = QueryRAGSkill()
    return _query_rag_skill


def get_query_with_selected_text_skill() -> QueryWithSelectedTextSkill:
    """
    Get the query with selected text skill instance
    """
    global _query_with_selected_text_skill
    if _query_with_selected_text_skill is None:
        _query_with_selected_text_skill = QueryWithSelectedTextSkill()
    return _query_with_selected_text_skill


def get_all_agent_skills() -> Dict[str, Any]:
    """
    Get all available agent skills
    """
    return {
        "retrieve_context": get_retrieve_context_skill(),
        "search_content": get_search_content_skill(),
        "answer_from_context": get_answer_from_context_skill(),
        "validate_grounding": get_validate_grounding_skill(),
        "get_rag_stats": get_rag_stats_skill(),
        "query_rag": get_query_rag_skill(),
        "query_with_selected_text": get_query_with_selected_text_skill()
    }