"""
LLM client configuration and setup
"""
import logging
from typing import Optional

from openai import AsyncOpenAI
from pydantic_settings import BaseSettings

from .claude_client import ClaudeClient, ClaudeSettings, get_claude_client, init_claude


logger = logging.getLogger(__name__)


class LLMSettings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo"
    openrouter_api_key: str = ""
    openrouter_model: str = "mistralai/devstral-2512:free"
    temperature: float = 0.7
    max_tokens: int = 1000

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"  # Ignore extra environment variables


class LLMClient:
    """
    OpenAI/OpenRouter client wrapper for LLM operations
    """

    def __init__(self, settings: Optional[LLMSettings] = None):
        self.settings = settings or LLMSettings()

        # Check for OpenRouter first (as it seems to be your preferred provider)
        if self.settings.openrouter_api_key:
            logger.info("Using OpenRouter API")
            self.client = AsyncOpenAI(
                api_key=self.settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = self.settings.openrouter_model
        elif self.settings.openai_api_key:
            logger.info("Using OpenAI API")
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            self.model = self.settings.openai_model
        else:
            logger.warning("No API key found (neither OpenAI nor OpenRouter). LLM functionality will not work.")
            self.client = AsyncOpenAI(api_key="")  # Will fail on actual calls
            self.model = self.settings.openrouter_model  # Default to OpenRouter model

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise


# Global instances
_llm_client: Optional[LLMClient] = None
_claude_client: Optional[ClaudeClient] = None


def get_llm_client() -> LLMClient:
    """
    Get the OpenAI LLM client instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def init_llm(settings: Optional[LLMSettings] = None) -> LLMClient:
    """
    Initialize the OpenAI LLM client
    """
    global _llm_client
    _llm_client = LLMClient(settings)
    logger.info("OpenAI LLM client initialized successfully")
    return _llm_client


def get_all_llm_clients():
    """
    Get both OpenAI and Claude clients
    """
    return {
        "openai": get_llm_client(),
        "claude": get_claude_client()
    }


def init_all_llm_clients(openai_settings: Optional[LLMSettings] = None,
                        claude_settings: Optional[ClaudeSettings] = None):
    """
    Initialize both OpenAI and Claude clients
    """
    init_llm(openai_settings)
    init_claude(claude_settings)
    logger.info("Both OpenAI and Claude clients initialized successfully")