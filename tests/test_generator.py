import pytest
from app.services.campaign_generator import CampaignService
from app.models.schemas import CreateCampaignRequest


def test_generate_campaign_multi_channel():
    service = CampaignService(provider_name="mock")
    req = CreateCampaignRequest(
        source_text="Release 3.0: High-throughput Kafka Stream Processing and Auto-Scaling Kubernetes workers.",
        campaign_title="Kafka Stream Processing v3.0",
        target_channels=["TWITTER_THREAD", "LINKEDIN_POST", "NEWSLETTER_DIGEST"]
    )
    campaign = service.generate_campaign(req)

    assert campaign.campaign_id.startswith("CMP-")
    assert campaign.title == "Kafka Stream Processing v3.0"
    assert len(campaign.posts) == 3
    assert any(p.channel == "TWITTER_THREAD" for p in campaign.posts)
    assert any(p.channel == "LINKEDIN_POST" for p in campaign.posts)
    assert any(p.channel == "NEWSLETTER_DIGEST" for p in campaign.posts)
    assert campaign.compliance.overall_score >= 85.0
    assert campaign.compliance.is_compliant is True
