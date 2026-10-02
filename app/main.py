import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.schemas import (
    Campaign,
    CreateCampaignRequest,
    VerifyContentRequest,
    ComplianceReport,
    ChannelPost
)
from app.models.database import db
from app.services.campaign_generator import CampaignService
from app.guardrails.evaluator import BrandComplianceEvaluator
from app.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="OmniBrand Copilot API",
    description="Multi-Channel Content Automation Studio with Brand Guardrails",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

campaign_service = CampaignService()
evaluator = BrandComplianceEvaluator()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse, tags=["Web Studio"])
def serve_studio_ui():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>OmniBrand Copilot API Active</h1><p>Visit /docs for OpenAPI documentation.</p>"


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "omni-brand-copilot",
        "provider": settings.LLM_PROVIDER,
        "environment": settings.ENVIRONMENT
    }


# Campaign Generation & Management
@app.post("/api/v1/campaigns", response_model=Campaign, status_code=status.HTTP_201_CREATED, tags=["Campaigns"])
def create_campaign(req: CreateCampaignRequest):
    campaign = campaign_service.generate_campaign(req)
    return campaign


@app.get("/api/v1/campaigns", response_model=List[Campaign], tags=["Campaigns"])
def list_campaigns():
    return db.list_campaigns()


@app.get("/api/v1/campaigns/{campaign_id}", response_model=Campaign, tags=["Campaigns"])
def get_campaign(campaign_id: str):
    c = db.get_campaign(campaign_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found."
        )
    return c


# Live Guardrail Verification Endpoint
@app.post("/api/v1/verify", response_model=ComplianceReport, tags=["Guardrails"])
def verify_content(req: VerifyContentRequest):
    post = ChannelPost(
        channel=req.channel,
        title="Custom Review Draft",
        content=req.content,
        character_count=len(req.content)
    )
    return evaluator.evaluate_posts([post], source_text=req.source_text or "")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
