"""
OpenAI Agent SDK Implementation for RAG Chatbot
"""
import os
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Initialize agents module variables
agents = None
Agent = None
Runner = None
OpenAIProvider = None
OpenAIChatCompletionsModel = None
function_tool = None

def _load_agents_module():
    """Dynamically load the agents module to avoid circular imports"""
    global agents, Agent, Runner, OpenAIProvider, OpenAIChatCompletionsModel, function_tool
    if agents is None:
        try:
            # Import the agents package - this may cause circular import in some contexts
            import agents
            Agent = agents.Agent
            Runner = agents.Runner
            OpenAIProvider = agents.OpenAIProvider
            OpenAIChatCompletionsModel = agents.OpenAIChatCompletionsModel
            function_tool = agents.function_tool
            agents = agents  # Store the actual agents module
        except ImportError as e:
            # If import fails, set to None to indicate unavailability
            logger.warning(f"Could not load agents module: {e}")
            agents = None
            Agent = None
            Runner = None
            OpenAIProvider = None
            OpenAIChatCompletionsModel = None
            function_tool = None

# Load the environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Get the OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Check if the API key is present; if not, raise an error
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set. Please ensure it is defined in your .env file.")

# Initialize OpenAI provider with OpenRouter base URL
from openai import AsyncOpenAI

# Create OpenAI client with OpenRouter base URL
openai_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Initialize OpenAI model
def _get_model():
    _load_agents_module()
    return OpenAIChatCompletionsModel(
        model="mistralai/devstral-2512:free",
        openai_client=openai_client
    )

def _get_provider():
    _load_agents_module()
    return OpenAIProvider(
        openai_client=openai_client
    )

# Defer model and provider initialization until they are first used
model = None
provider = None

def get_model():
    global model
    if model is None:
        model = _get_model()
    return model

def get_provider():
    global provider
    if provider is None:
        provider = _get_provider()
    return provider

# Define Pydantic models for tool parameters
class RetrieveContextParams(BaseModel):
    query: str = Field(..., description="The query to search for in the knowledge base")
    top_k: int = Field(default=5, description="Number of results to return")


class SearchContentParams(BaseModel):
    query: str = Field(..., description="The query to search for in the knowledge base")
    top_k: int = Field(default=10, description="Number of results to return")


class ContextItem(BaseModel):
    """Represents a single context item for the agent tools"""
    id: Optional[str] = Field(default=None, description="Unique identifier for the context item")
    content: str = Field(..., description="The content of the context item")
    source: Optional[str] = Field(default=None, description="Source of the context item")
    similarity: Optional[float] = Field(default=None, description="Similarity score of the context item")


class AnswerFromContextParams(BaseModel):
    query: str = Field(..., description="The original query")
    context: List[ContextItem] = Field(..., description="List of context items to use for answering")
    system_prompt: Optional[str] = Field(default=None, description="Optional system prompt to guide the response")


class ValidateGroundingParams(BaseModel):
    response: str = Field(..., description="The response to validate")
    context: List[ContextItem] = Field(..., description="The context that should ground the response")


class QueryRAGParams(BaseModel):
    query: str = Field(..., description="The query to process")
    top_k: int = Field(default=5, description="Number of results to retrieve")
    validate_grounding: bool = Field(default=True, description="Whether to validate grounding")


class QueryWithSelectedTextParams(BaseModel):
    query: str = Field(..., description="The query to process")
    selected_text: str = Field(..., description="The selected text to use as primary context")
    top_k: int = Field(default=5, description="Number of additional results to retrieve")
    validate_grounding: bool = Field(default=True, description="Whether to validate grounding")


# Import the skills
try:
    # Try relative import first (when used as part of package)
    from .openai_agent_skills import (
        get_retrieve_context_skill,
        get_search_content_skill,
        get_answer_from_context_skill,
        get_validate_grounding_skill,
        get_rag_stats_skill,
        get_query_rag_skill,
        get_query_with_selected_text_skill
    )
except ImportError:
    # Fall back to absolute import (when run directly)
    from src.agents.openai_agent_skills import (
        get_retrieve_context_skill,
        get_search_content_skill,
        get_answer_from_context_skill,
        get_validate_grounding_skill,
        get_rag_stats_skill,
        get_query_rag_skill,
        get_query_with_selected_text_skill
    )


# Define tools using the OpenAI Agents framework
def create_retrieve_context_tool():
    """Create the retrieve context tool"""
    _load_agents_module()
    async def execute(params: RetrieveContextParams) -> List[Dict[str, Any]]:
        try:
            skill = get_retrieve_context_skill()
            result = await skill.execute(params.query, params.top_k)
            return result
        except Exception as e:
            logger.error(f"Error in retrieve_context_tool: {e}")
            return []

    return function_tool(
        name_override="retrieve_context",
        description_override="Retrieve relevant context from the knowledge base",
    )(execute)


def create_search_content_tool():
    """Create the search content tool"""
    _load_agents_module()
    async def execute(params: SearchContentParams) -> List[Dict[str, Any]]:
        try:
            skill = get_search_content_skill()
            result = await skill.execute(params.query, params.top_k)
            return result
        except Exception as e:
            logger.error(f"Error in search_content_tool: {e}")
            return []

    return function_tool(
        name_override="search_content",
        description_override="Search for content in the knowledge base",
    )(execute)


def create_answer_from_context_tool():
    """Create the answer from context tool"""
    _load_agents_module()
    async def execute(params: AnswerFromContextParams) -> str:
        try:
            # Convert ContextItem objects to the format expected by the skill
            context_list = [
                {
                    "id": item.id,
                    "content": item.content,
                    "source": item.source,
                    "similarity": item.similarity
                }
                for item in params.context
            ]

            skill = get_answer_from_context_skill()
            result = await skill.execute(params.query, context_list, params.system_prompt)
            return result
        except Exception as e:
            logger.error(f"Error in answer_from_context_tool: {e}")
            return "Sorry, I encountered an error while generating an answer."

    return function_tool(
        name_override="answer_from_context",
        description_override="Generate answers based on provided context",
    )(execute)


def create_validate_grounding_tool():
    """Create the validate grounding tool"""
    _load_agents_module()
    async def execute(params: ValidateGroundingParams) -> float:
        try:
            # Convert ContextItem objects to the format expected by the skill
            context_list = [
                {
                    "id": item.id,
                    "content": item.content,
                    "source": item.source,
                    "similarity": item.similarity
                }
                for item in params.context
            ]

            skill = get_validate_grounding_skill()
            result = await skill.execute(params.response, context_list)
            return result
        except Exception as e:
            logger.error(f"Error in validate_grounding_tool: {e}")
            return 0.0

    return function_tool(
        name_override="validate_grounding",
        description_override="Validate that responses are grounded in provided context",
    )(execute)


def create_get_rag_stats_tool():
    """Create the get RAG stats tool"""
    _load_agents_module()
    async def execute() -> Dict[str, Any]:
        try:
            skill = get_rag_stats_skill()
            result = await skill.execute()
            return result
        except Exception as e:
            logger.error(f"Error in get_rag_stats_tool: {e}")
            return {"error": str(e)}

    return function_tool(
        name_override="get_rag_stats",
        description_override="Get statistics about the RAG system",
    )(execute)


def create_query_rag_tool():
    """Create the query RAG tool"""
    _load_agents_module()
    async def execute(params: QueryRAGParams) -> Dict[str, Any]:
        try:
            skill = get_query_rag_skill()
            result = await skill.execute(params.query, params.top_k, params.validate_grounding)
            return result
        except Exception as e:
            logger.error(f"Error in query_rag_tool: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your query.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "error": str(e)
            }

    return function_tool(
        name_override="query_rag",
        description_override="Perform a complete RAG query",
    )(execute)


def create_query_with_selected_text_tool():
    """Create the query with selected text tool"""
    _load_agents_module()
    async def execute(params: QueryWithSelectedTextParams) -> Dict[str, Any]:
        try:
            skill = get_query_with_selected_text_skill()
            result = await skill.execute(params.query, params.selected_text, params.top_k, params.validate_grounding)
            return result
        except Exception as e:
            logger.error(f"Error in query_with_selected_text_tool: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your query.",
                "context_used": [],
                "grounding_confidence": 0.0,
                "error": str(e)
            }

    return function_tool(
        name_override="query_with_selected_text",
        description_override="Perform a query using selected text as primary context",
    )(execute)


class RAGAgent:
    """
    Main RAG Agent using OpenAI Agent SDK with OpenRouter
    """

    def __init__(self, name: str = "RAG Assistant",
                 instructions: str = "You are a helpful RAG assistant that answers questions based on provided book content. Use the available tools to search for information and provide accurate answers."):
        _load_agents_module()
        self.name = name
        self.instructions = instructions

        # Create tools
        self.retrieve_context_tool = create_retrieve_context_tool()
        self.search_content_tool = create_search_content_tool()
        self.answer_from_context_tool = create_answer_from_context_tool()
        self.validate_grounding_tool = create_validate_grounding_tool()
        self.get_rag_stats_tool = create_get_rag_stats_tool()
        self.query_rag_tool = create_query_rag_tool()
        self.query_with_selected_text_tool = create_query_with_selected_text_tool()

        # Create the agent with tools
        self.agent = Agent(
            name=name,
            instructions=instructions,
            model=get_model(),  # Use the model instead of provider
            tools=[
                self.retrieve_context_tool,
                self.search_content_tool,
                self.answer_from_context_tool,
                self.validate_grounding_tool,
                self.get_rag_stats_tool,
                self.query_rag_tool,
                self.query_with_selected_text_tool
            ]
        )

    async def process_query(self, query: str) -> str:
        """
        Process a user query using the agent

        Args:
            query: The user's query

        Returns:
            The agent's response
        """
        _load_agents_module()
        try:
            logger.info(f"Processing query with RAG Agent: {query[:50]}...")

            # Run the agent with the query
            result = await Runner.run(self.agent, query)
            # Extract the response from the RunResult object
            # The output is stored in result.final_output or result.output depending on the version
            if hasattr(result, 'final_output'):
                response = result.final_output
            elif hasattr(result, 'output'):
                response = result.output
            elif hasattr(result, 'content'):
                response = result.content
            elif hasattr(result, '__dict__') and 'output' in result.__dict__:
                response = result.__dict__['output']
            else:
                # For different versions of the agents library, the output might be structured differently
                response = str(result) if result else "No response from agent"

            logger.info(f"Agent processed query successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing query with agent: {e}")
            return "Sorry, I encountered an error while processing your query."

    async def process_query_with_context(self, query: str, context: Optional[str] = None) -> str:
        """
        Process a user query with additional context

        Args:
            query: The user's query
            context: Additional context to provide to the agent

        Returns:
            The agent's response
        """
        _load_agents_module()
        try:
            logger.info(f"Processing query with context using RAG Agent: {query[:50]}...")

            # Prepare the full prompt with context if provided
            if context:
                full_query = f"Context: {context}\n\nQuestion: {query}"
            else:
                full_query = query

            # Run the agent with the query
            result = await Runner.run(self.agent, full_query)
            # Extract the response from the RunResult object
            # The output is stored in result.final_output or result.output depending on the version
            if hasattr(result, 'final_output'):
                response = result.final_output
            elif hasattr(result, 'output'):
                response = result.output
            elif hasattr(result, 'content'):
                response = result.content
            elif hasattr(result, '__dict__') and 'output' in result.__dict__:
                response = result.__dict__['output']
            else:
                # For different versions of the agents library, the output might be structured differently
                response = str(result) if result else "No response from agent"

            logger.info(f"Agent processed query with context successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing query with context using agent: {e}")
            return "Sorry, I encountered an error while processing your query."

    async def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the agent

        Returns:
            Dictionary with agent statistics
        """
        try:
            stats = {
                "name": self.name,
                "model": "mistralai/devstral-2512:free",
                "provider": "OpenRouter",
                "status": "active",
                "tools_available": [
                    "retrieve_context",
                    "search_content",
                    "answer_from_context",
                    "validate_grounding",
                    "get_rag_stats",
                    "query_rag",
                    "query_with_selected_text"
                ]
            }

            logger.info("Retrieved agent statistics")
            return stats
        except Exception as e:
            logger.error(f"Error retrieving agent stats: {e}")
            return {"error": str(e)}


class RAGAgentManager:
    """
    Manager class to handle multiple RAG agents
    """

    def __init__(self):
        self.agents: Dict[str, RAGAgent] = {}
        self.default_agent: Optional[RAGAgent] = None

    def create_agent(self, name: str, instructions: str = None) -> RAGAgent:
        """
        Create a new RAG agent

        Args:
            name: Name of the agent
            instructions: Custom instructions for the agent

        Returns:
            The created RAG agent
        """
        try:
            agent = RAGAgent(name=name, instructions=instructions or "You are a helpful RAG assistant that answers questions based on provided book content. Use the available tools to search for information and provide accurate answers. Always cite sources when possible and be transparent about limitations when the provided context doesn't contain sufficient information to answer the question.")
            self.agents[name] = agent

            # Set as default if it's the first agent
            if not self.default_agent:
                self.default_agent = agent

            logger.info(f"Created RAG agent: {name}")
            return agent
        except Exception as e:
            logger.error(f"Error creating RAG agent '{name}': {e}")
            raise

    def get_agent(self, name: str) -> Optional[RAGAgent]:
        """
        Get an existing agent by name

        Args:
            name: Name of the agent

        Returns:
            The agent if found, None otherwise
        """
        return self.agents.get(name)

    def get_default_agent(self) -> Optional[RAGAgent]:
        """
        Get the default agent

        Returns:
            The default agent
        """
        if self.default_agent is None:
            try:
                # Create the default agent if it doesn't exist
                self.default_agent = self.create_agent(
                    name="RAG Assistant",
                    instructions="You are a helpful RAG assistant that answers questions based on provided book content. Use the available tools to search for information and provide accurate answers. Always cite sources when possible and be transparent about limitations when the provided context doesn't contain sufficient information to answer the question."
                )
            except Exception as e:
                # If agent creation fails due to circular import or other issues, return None
                logger.error(f"Failed to create RAG agent: {e}")
                return None
        return self.default_agent

    async def process_query(self, query: str, agent_name: str = None) -> str:
        """
        Process a query using the specified agent or default agent

        Args:
            query: The user's query
            agent_name: Name of the agent to use (optional)

        Returns:
            The agent's response
        """
        agent = self.get_agent(agent_name) if agent_name else self.get_default_agent()

        if not agent:
            logger.error("No agent available to process query")
            return "Sorry, no agent is available to process your query."

        return await agent.process_query(query)

    async def process_query_with_context(self, query: str, context: str = None, agent_name: str = None) -> str:
        """
        Process a query with context using the specified agent or default agent

        Args:
            query: The user's query
            context: Additional context to provide
            agent_name: Name of the agent to use (optional)

        Returns:
            The agent's response
        """
        agent = self.get_agent(agent_name) if agent_name else self.get_default_agent()

        if not agent:
            logger.error("No agent available to process query")
            return "Sorry, no agent is available to process your query."

        return await agent.process_query_with_context(query, context)


# Global instance
_rag_agent_manager: Optional[RAGAgentManager] = None


def get_rag_agent_manager() -> RAGAgentManager:
    """
    Get the RAG agent manager instance
    """
    global _rag_agent_manager
    if _rag_agent_manager is None:
        _rag_agent_manager = RAGAgentManager()
        # Don't create the default agent immediately to avoid circular import
        # The default agent will be created when first accessed

    return _rag_agent_manager


def get_default_rag_agent() -> Optional[RAGAgent]:
    """
    Get the default RAG agent
    """
    manager = get_rag_agent_manager()
    return manager.get_default_agent()


async def run_sample_query():
    """
    Run a sample query to test the agent
    """
    manager = get_rag_agent_manager()
    result = await manager.process_query("Hello, can you help me understand how RAG works?")
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_sample_query())