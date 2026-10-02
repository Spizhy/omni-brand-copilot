import uuid
import re
from typing import Optional, List
from app.models.schemas import Campaign, CreateCampaignRequest, ComplianceReport
from app.providers import get_content_provider
from app.guardrails.evaluator import BrandComplianceEvaluator
from app.models.database import db
from app.utils.logger import get_logger

logger = get_logger("campaign_generator")


class CampaignService:
    def __init__(self, provider_name: Optional[str] = None):
        self.provider = get_content_provider(provider_name)
        self.evaluator = BrandComplianceEvaluator()

    def generate_campaign(self, req: CreateCampaignRequest) -> Campaign:
        campaign_id = f"CMP-{uuid.uuid4().hex[:8].upper()}"
        logger.info("Generating campaign %s", campaign_id)

        # 1. Determine Title
        title = req.campaign_title
        if not title:
            first_line = req.source_text.strip().splitlines()[0]
            title = re.sub(r"^[#\s]+", "", first_line)[:60]

        # 2. Multi-channel AI generation
        posts = self.provider.generate_multi_channel(
            source_text=req.source_text,
            target_channels=req.target_channels
        )

        # 3. Automated Brand Compliance Evaluation
        compliance: ComplianceReport = self.evaluator.evaluate_posts(
            posts=posts,
            source_text=req.source_text
        )

        campaign = Campaign(
            campaign_id=campaign_id,
            title=title,
            source_content=req.source_text,
            posts=posts,
            compliance=compliance
        )

        # 4. Save to Database
        db.save_campaign(campaign)
        logger.info(
            "Campaign %s created. Compliance Score: %.1f%% (Compliant: %s)",
            campaign_id,
            compliance.overall_score,
            compliance.is_compliant
        )
        return campaign
