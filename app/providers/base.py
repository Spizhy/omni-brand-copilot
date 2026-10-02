from abc import ABC, abstractmethod
from typing import List
from app.models.schemas import ChannelPost, ChannelType


class BaseContentLLMProvider(ABC):
    @abstractmethod
    def generate_multi_channel(
        self,
        source_text: str,
        target_channels: List[ChannelType]
    ) -> List[ChannelPost]:
        """Generate channel-optimized posts from long-form source text."""
        pass
