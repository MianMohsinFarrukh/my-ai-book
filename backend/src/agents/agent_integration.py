"""
Integration layer between OpenAI Agent SDK and existing RAG functionality
"""
import logging
from typing import Dict, Any, Optional, List
from src.services.rag_service import get_rag_service
from .openai_agent import get_rag_agent_manager, RAGAgent

logger = logging.getLogger(__name__)


class AgentChatService:
    """
    Service to integrate RAG functionality with the chat API
    """

    def __init__(self):
        self.rag_service = get_rag_service()
        # Temporarily disable agent manager due to circular import issues
        # self.agent_manager = get_rag_agent_manager()
        self.agent_manager = None

    async def process_chat_message(self, query: str, session_id: str = None, selected_text: str = None) -> Dict[str, Any]:
        """
        Process a chat message using direct RAG service (agent functionality disabled due to circular import issues)

        Args:
            query: The user's query
            session_id: Optional session ID for conversation history
            selected_text: Optional selected text for context

        Returns:
            Dictionary with response and metadata
        """
        try:
            logger.info(f"Processing chat message with direct RAG service: {query[:50]}...")

            # Always use direct RAG service due to agent system issues
            return await self._process_with_direct_rag(query, selected_text, session_id)

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your message.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "agent_used": "direct_rag_service",
                "session_id": session_id,
                "error": str(e)
            }

    async def _process_with_direct_rag(self, query: str, selected_text: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Process chat message using direct RAG service as fallback
        """
        try:
            if selected_text:
                # Use query with selected text
                result = await self.rag_service.query_with_selected_text(
                    query=query,
                    selected_text=selected_text,
                    top_k=5,
                    validate_grounding=True
                )
            else:
                # Use regular RAG query
                result = await self.rag_service.query(
                    query=query,
                    top_k=5,
                    validate_grounding=True
                )

            # Ensure result has the expected structure
            if isinstance(result, dict):
                response = result.get("response", result.get("answer", "I couldn't find a good answer for your question."))
                context_used = result.get("context_used", [])
                grounding_confidence = result.get("grounding_confidence", 0.0)
            else:
                response = str(result) if result else "I couldn't find a good answer for your question."
                context_used = []
                grounding_confidence = 0.0

            return {
                "response": response,
                "context_used": context_used,
                "grounding_confidence": grounding_confidence,
                "agent_used": "direct_rag_service",
                "session_id": session_id,
                "timestamp": None
            }

        except Exception as e:
            logger.error(f"Error in direct RAG fallback: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your message.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "agent_used": "direct_rag_service",
                "session_id": session_id,
                "error": str(e)
            }

    async def process_rag_query(self, query: str, top_k: int = 5, validate_grounding: bool = True) -> Dict[str, Any]:
        """
        Process a RAG query using the agent's tools directly

        Args:
            query: The query to process
            top_k: Number of results to retrieve
            validate_grounding: Whether to validate grounding

        Returns:
            Dictionary with response and context
        """
        try:
            logger.info(f"Processing RAG query with agent tools: {query[:50]}...")

            # Get the default agent
            agent = self.agent_manager.get_default_agent()
            if not agent:
                raise Exception("No agent available")

            # Use the agent's query RAG tool through the agent's process methods
            # For now, we'll create a query that uses the appropriate tools
            query_text = f"Process this RAG query: '{query}' with top_k={top_k} and validate_grounding={validate_grounding}. Use the query_rag tool."

            response = await agent.process_query(query_text)

            # The response will be the agent's output, which may include context and grounding info
            result = {
                "response": response,
                "context_used": [],  # This would need to be extracted from the agent's response
                "grounding_confidence": 0.0  # This would need to be extracted from the agent's response
            }

            logger.info(f"Agent processed RAG query successfully")
            return result

        except Exception as e:
            logger.error(f"Error processing RAG query with agent: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your query.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "error": str(e)
            }

    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the status of the agent system

        Returns:
            Dictionary with agent status information
        """
        try:
            agent = self.agent_manager.get_default_agent()
            if not agent:
                return {
                    "status": "error",
                    "message": "No agent available"
                }

            stats = await agent.get_agent_stats()
            stats["status"] = "active"

            return stats
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


class AgentIngestionService:
    """
    Service to integrate the OpenAI Agent with the ingestion functionality
    """

    def __init__(self):
        self.agent_manager = get_rag_agent_manager()

    async def process_ingestion_status(self, ingestion_result: Dict[str, Any]) -> str:
        """
        Process ingestion results and generate a summary using the agent

        Args:
            ingestion_result: The result from the ingestion process

        Returns:
            Summary of the ingestion process
        """
        try:
            logger.info("Processing ingestion status with agent")

            agent = self.agent_manager.get_default_agent()
            if not agent:
                raise Exception("No agent available")

            # Create a summary query for the agent
            summary_query = (
                f"Please provide a summary of this ingestion process: "
                f"Files processed: {ingestion_result.get('files_processed', 0)}, "
                f"Chunks created: {ingestion_result.get('chunks_created', 0)}, "
                f"Status: {ingestion_result.get('status', 'unknown')}. "
                f"Please explain what this means for the knowledge base."
            )

            response = await agent.process_query(summary_query)
            return response

        except Exception as e:
            logger.error(f"Error processing ingestion status with agent: {e}")
            return f"Ingestion completed with {ingestion_result.get('files_processed', 0)} files and {ingestion_result.get('chunks_created', 0)} chunks created."


# Global instances
_agent_chat_service: Optional[AgentChatService] = None
_agent_ingestion_service: Optional[AgentIngestionService] = None


def get_agent_chat_service() -> AgentChatService:
    """
    Get the agent chat service instance
    """
    global _agent_chat_service
    if _agent_chat_service is None:
        _agent_chat_service = AgentChatService()
    return _agent_chat_service


def get_agent_ingestion_service() -> AgentIngestionService:
    """
    Get the agent ingestion service instance
    """
    global _agent_ingestion_service
    if _agent_ingestion_service is None:
        _agent_ingestion_service = AgentIngestionService()
    return _agent_ingestion_service


# Update the __init__.py to include the new module
def update_api_with_agent_support():
    """
    Function to update the API with agent support
    This would typically be called during application startup
    """
    logger.info("Initializing agent integration with API")

    # Initialize the agent manager to ensure agents are created
    agent_manager = get_rag_agent_manager()
    default_agent = agent_manager.get_default_agent()

    if default_agent:
        logger.info(f"Agent '{default_agent.name}' initialized and ready")
    else:
        logger.error("Failed to initialize agent")