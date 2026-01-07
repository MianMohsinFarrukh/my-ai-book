"""
RAG Chatbot Agents Package

This package contains various agent implementations for the RAG chatbot:
- subagents.py: Claude Code Subagents implementation
- skills.py: Agent Skills implementation for reusable functionality
- openai_agent_skills.py: OpenAI Agent SDK Skills for RAG Chatbot
- openai_agent.py: OpenAI Agent SDK Implementation for RAG Chatbot
"""

from .subagents import (
    SubAgent,
    IngestionSubAgent,
    RetrievalSubAgent,
    ResponseGuardSubAgent,
    get_ingestion_subagent,
    get_retrieval_subagent,
    get_response_guard_subagent,
    get_all_subagents
)

from .skills import (
    AgentSkill,
    RetrieveContextSkill,
    AnswerFromContextSkill,
    ValidateGroundingSkill,
    get_retrieve_context_skill,
    get_answer_from_context_skill,
    get_validate_grounding_skill,
    get_all_skills
)

from .openai_agent_skills import (
    RetrieveContextSkill as OpenAIRetrieveContextSkill,
    SearchContentSkill,
    AnswerFromContextSkill as OpenAIAnswerFromContextSkill,
    ValidateGroundingSkill as OpenAIValidateGroundingSkill,
    GetRAGStatsSkill,
    QueryRAGSkill,
    QueryWithSelectedTextSkill,
    get_retrieve_context_skill as get_openai_retrieve_context_skill,
    get_search_content_skill,
    get_answer_from_context_skill as get_openai_answer_from_context_skill,
    get_validate_grounding_skill as get_openai_validate_grounding_skill,
    get_rag_stats_skill,
    get_query_rag_skill,
    get_query_with_selected_text_skill,
    get_all_agent_skills as get_all_openai_agent_skills
)

from .openai_agent import (
    RAGAgent,
    RAGAgentManager,
    get_rag_agent_manager,
    get_default_rag_agent
)

# Import agent_integration at the end to avoid circular imports
# This is imported in the update_api_with_agent_support function
# which is called during application startup

__all__ = [
    # Original subagents
    "SubAgent",
    "IngestionSubAgent",
    "RetrievalSubAgent",
    "ResponseGuardSubAgent",
    "get_ingestion_subagent",
    "get_retrieval_subagent",
    "get_response_guard_subagent",
    "get_all_subagents",

    # Original skills
    "AgentSkill",
    "RetrieveContextSkill",
    "AnswerFromContextSkill",
    "ValidateGroundingSkill",
    "get_retrieve_context_skill",
    "get_answer_from_context_skill",
    "get_validate_grounding_skill",
    "get_all_skills",

    # OpenAI Agent SDK skills
    "OpenAIRetrieveContextSkill",
    "SearchContentSkill",
    "OpenAIAnswerFromContextSkill",
    "OpenAIValidateGroundingSkill",
    "GetRAGStatsSkill",
    "QueryRAGSkill",
    "QueryWithSelectedTextSkill",
    "get_openai_retrieve_context_skill",
    "get_search_content_skill",
    "get_openai_answer_from_context_skill",
    "get_openai_validate_grounding_skill",
    "get_rag_stats_skill",
    "get_query_rag_skill",
    "get_query_with_selected_text_skill",
    "get_all_openai_agent_skills",

    # OpenAI Agent SDK
    "RAGAgent",
    "RAGAgentManager",
    "get_rag_agent_manager",
    "get_default_rag_agent",

]