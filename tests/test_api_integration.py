import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_serve_studio_ui():
    res = client.get("/")
    assert res.status_code == 200
    assert "OmniBrand Copilot" in res.text
    assert "Brand Constitution Audit" in res.text


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "omni-brand-copilot"


def test_create_and_get_campaign():
    payload = {
        "source_text": "Release 4.0 delivers zero-copy in-memory caching for low-latency APIs across microservices.",
        "campaign_title": "Zero-Copy In-Memory Caching v4.0",
        "target_channels": ["TWITTER_THREAD", "LINKEDIN_POST"]
    }
    res = client.post("/api/v1/campaigns", json=payload)
    assert res.status_code == 201
    campaign = res.json()
    assert campaign["campaign_id"].startswith("CMP-")
    assert len(campaign["posts"]) == 2

    # Query get endpoint
    cid = campaign["campaign_id"]
    get_res = client.get(f"/api/v1/campaigns/{cid}")
    assert get_res.status_code == 200
    assert get_res.json()["campaign_id"] == cid


def test_verify_endpoint():
    payload = {
        "channel": "LINKEDIN_POST",
        "content": "This is our revolutionary game-changing product update.",
        "source_text": "Some source"
    }
    res = client.post("/api/v1/verify", json=payload)
    assert res.status_code == 200
    report = res.json()
    assert report["overall_score"] < 100.0
    assert len(report["violations"]) >= 1
