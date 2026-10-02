from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

ChannelType = Literal[
    "TWITTER_THREAD",
    "LINKEDIN_POST",
    "NEWSLETTER_DIGEST",
    "EXECUTIVE_ANNOUNCEMENT"
]

ViolationSeverity = Literal["CRITICAL", "WARNING"]


class ChannelPost(BaseModel):
    channel: ChannelType
    title: str
    content: str
    character_count: int
    tags: List[str] = Field(default_factory=list)


class RuleViolation(BaseModel):
    rule_name: str
    severity: ViolationSeverity
    message: str
    offending_text: Optional[str] = None


class ComplianceReport(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0)
    is_compliant: bool
    violations: List[RuleViolation] = Field(default_factory=list)
    checks_performed: List[str] = Field(default_factory=list)


class Campaign(BaseModel):
    campaign_id: str
    title: str
    source_content: str
    posts: List[ChannelPost]
    compliance: ComplianceReport
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CreateCampaignRequest(BaseModel):
    source_text: str = Field(..., min_length=20, description="Long-form release notes, whitepaper or announcement")
    campaign_title: Optional[str] = Field(default=None, description="Campaign title or headline")
    target_channels: Optional[List[ChannelType]] = Field(default=None, description="Channels to generate for")


class VerifyContentRequest(BaseModel):
    channel: ChannelType
    content: str
    source_text: Optional[str] = None
