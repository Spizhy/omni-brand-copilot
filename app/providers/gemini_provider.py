import json
from typing import List, Optional
import httpx
from app.config import settings
from app.models.schemas import ChannelPost, ChannelType
from app.providers.base import BaseContentLLMProvider


class GeminiContentProvider(BaseContentLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or "gemini-1.5-flash"

    def generate_multi_channel(self, source_text: str, target_channels: List[ChannelType]) -> List[ChannelPost]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        channels = target_channels or ["TWITTER_THREAD", "LINKEDIN_POST", "NEWSLETTER_DIGEST"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            f"You are a brand copywriter. Generate tailored social & announcement posts from this source text for {channels}.\n"
            f"Return JSON with key 'posts' containing list with fields: channel, title, content, character_count, tags.\n\n"
            f"Source Text:\n{source_text}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        with httpx.Client(timeout=35.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            posts_json = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])["posts"]
            return [ChannelPost.model_validate(p) for p in posts_json]
