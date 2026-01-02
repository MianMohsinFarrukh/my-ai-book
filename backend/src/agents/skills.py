"""
Agent Skills implementation for reusable functionality
"""
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ..services.rag_service import get_rag_service
from ..services.embedding_service import get_embedding_service


logger = logging.getLogger(__name__)


class AgentSkill(ABC):
    """
    Abstract base class for agent skills
    """

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the skill with given parameters
        """
        pass


class RetrieveContextSkill(AgentSkill):
    """
    Skill to retrieve relevant context from the vector database
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
            return context
        except Exception as e:
            logger.error(f"Error in retrieve_context skill: {e}")
            return []


class AnswerFromContextSkill(AgentSkill):
    """
    Skill to generate answers based on provided context
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


class ValidateGroundingSkill(AgentSkill):
    """
    Skill to validate that responses are grounded in provided context
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


# Global instances for the skills
_retrieve_context_skill: Optional[RetrieveContextSkill] = None
_answer_from_context_skill: Optional[AnswerFromContextSkill] = None
_validate_grounding_skill: Optional[ValidateGroundingSkill] = None


def get_retrieve_context_skill() -> RetrieveContextSkill:
    """
    Get the retrieve context skill instance
    """
    global _retrieve_context_skill
    if _retrieve_context_skill is None:
        _retrieve_context_skill = RetrieveContextSkill()
    return _retrieve_context_skill


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


# Convenience function to get all skills
def get_all_skills() -> Dict[str, AgentSkill]:
    """
    Get all available agent skills
    """
    return {
        "retrieve_context": get_retrieve_context_skill(),
        "answer_from_context": get_answer_from_context_skill(),
        "validate_grounding": get_validate_grounding_skill()
    }