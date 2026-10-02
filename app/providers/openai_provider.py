import json
from typing import List, Optional
import httpx
from app.config import settings
from app.models.schemas import ChannelPost, ChannelType
from app.providers.base import BaseContentLLMProvider

SYSTEM_PROMPT = """You are an expert multi-channel content marketer and brand copywriter.
Convert the provided source text into distinct channel adaptations:
1. TWITTER_THREAD (punchy thread chunks separated by double newlines)
2. LINKEDIN_POST (engaging professional narrative with bullet points and hashtags)
3. NEWSLETTER_DIGEST (structured Markdown summary)
4. EXECUTIVE_ANNOUNCEMENT (clean formal announcement)

Avoid banned hyperbole: Do NOT use 'game-changing', 'revolutionary', 'disruptive', or 'silver bullet'. Keep claims grounded in the source."""

class OpenAIContentProvider(BaseContentLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.LLM_MODEL or "gpt-4o-mini"

    def generate_multi_channel(self, source_text: str, target_channels: List[ChannelType]) -> List[ChannelPost]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        channels = target_channels or ["TWITTER_THREAD", "LINKEDIN_POST", "NEWSLETTER_DIGEST"]
        schema = {
            "type": "object",
            "properties": {
                "posts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string", "enum": channels},
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "character_count": {"type": "integer"},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["channel", "title", "content", "character_count"]
                    }
                }
            },
            "required": ["posts"]
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Source document:\n\n{source_text}\n\nGenerate for channels: {channels}"}
            ],
            "response_format": {"type": "json_schema", "json_schema": {"name": "multi_channel", "schema": schema}},
            "temperature": 0.4
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=35.0) as client:
            res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            posts_json = json.loads(data["choices"][0]["message"]["content"])["posts"]
            return [ChannelPost.model_validate(p) for p in posts_json]
