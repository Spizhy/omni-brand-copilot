from app.config import settings
from app.providers.base import BaseContentLLMProvider
from app.providers.mock_provider import MockContentLLMProvider
from app.providers.openai_provider import OpenAIContentProvider
from app.providers.gemini_provider import GeminiContentProvider


def get_content_provider(override_name: str = None) -> BaseContentLLMProvider:
    name = (override_name or settings.LLM_PROVIDER).lower()
    if name == "mock":
        return MockContentLLMProvider()
    elif name == "openai":
        return OpenAIContentProvider()
    elif name == "gemini":
        return GeminiContentProvider()
    return MockContentLLMProvider()
