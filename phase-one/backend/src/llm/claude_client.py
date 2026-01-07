"""
Claude API client configuration and setup
"""
import logging
from typing import Optional, List, Dict, Any
import httpx
from pydantic import BaseModel

from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)


class ClaudeSettings(BaseSettings):
    claude_api_key: str = ""
    claude_model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 1000

    class Config:
        env_file = ".env"
        env_prefix = "CLAUDE_"
        extra = "ignore"  # Ignore extra environment variables


class ClaudeMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ClaudeClient:
    """
    Claude API client wrapper for Anthropic operations
    """

    def __init__(self, settings: Optional[ClaudeSettings] = None):
        self.settings = settings or ClaudeSettings()

        if not self.settings.claude_api_key:
            logger.warning("Claude API key not found. Claude functionality will not work.")

        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.settings.claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Generate a response from Claude
        """
        url = f"{self.base_url}/messages"

        payload = {
            "model": self.settings.claude_model,
            "messages": messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
        }

        if system_prompt:
            payload["system"] = system_prompt

        if stream:
            payload["stream"] = True

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code != 200:
                    logger.error(f"Claude API error: {response.status_code} - {response.text}")
                    raise Exception(f"Claude API error: {response.status_code}")

                result = response.json()
                return result["content"][0]["text"] if result.get("content") else ""

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

    async def generate_with_context(
        self,
        query: str,
        context: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response with specific context
        """
        # Format context into a message
        context_str = ""
        for i, item in enumerate(context):
            context_str += f"Context {i+1}:\n"
            context_str += f"Source: {item.get('source', 'Unknown')}\n"
            context_str += f"Content: {item.get('content', '')}\n\n"

        full_prompt = f"Please answer the following question based on the provided context:\n\n"
        if context_str:
            full_prompt += f"Context:\n{context_str}\n"
        full_prompt += f"Question: {query}\n\n"
        full_prompt += "Answer: "

        messages = [{"role": "user", "content": full_prompt}]

        return await self.generate_response(messages, system_prompt)

    async def validate_response_grounding(
        self,
        response: str,
        context: List[Dict[str, Any]]
    ) -> float:
        """
        Validate that the response is grounded in the provided context
        """
        validation_prompt = f"""
        Please evaluate if the following response is factually consistent with the provided context.
        The response should only contain information that can be directly inferred from the context.
        Do not allow any hallucinations or made-up information.

        Context:
        {chr(10).join([item.get('content', '') for item in context])}

        Response to validate:
        {response}

        Please respond with a confidence score between 0 and 1, where 1 means fully consistent and 0 means completely inconsistent.
        Only return the number, nothing else.
        """

        messages = [{"role": "user", "content": validation_prompt}]
        result = await self.generate_response(messages)

        try:
            # Extract the confidence score from the response
            score = float(result.strip())
            return min(1.0, max(0.0, score))  # Clamp between 0 and 1
        except ValueError:
            logger.warning(f"Could not parse confidence score from Claude response: {result}")
            return 0.5  # Default to medium confidence if parsing fails


# Global instance
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """
    Get the Claude client instance
    """
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client


def init_claude(settings: Optional[ClaudeSettings] = None) -> ClaudeClient:
    """
    Initialize the Claude client
    """
    global _claude_client
    _claude_client = ClaudeClient(settings)
    logger.info("Claude client initialized successfully")
    return _claude_client