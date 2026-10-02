import os
import sqlite3
from typing import List, Optional
from app.config import settings
from app.models.schemas import Campaign
from app.utils.logger import get_logger

logger = get_logger("database")


class CampaignDatabase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    compliance_score REAL NOT NULL,
                    is_compliant INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );
            """)
            conn.commit()

    def save_campaign(self, campaign: Campaign):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO campaigns 
                (campaign_id, title, compliance_score, is_compliant, created_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                campaign.campaign_id,
                campaign.title,
                campaign.compliance.overall_score,
                1 if campaign.compliance.is_compliant else 0,
                campaign.created_at,
                campaign.model_dump_json()
            ))
            conn.commit()

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM campaigns WHERE campaign_id = ?", (campaign_id,))
            row = cur.fetchone()
            if row:
                return Campaign.model_validate_json(row["data_json"])
            return None

    def list_campaigns(self, limit: int = 20) -> List[Campaign]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT data_json FROM campaigns ORDER BY created_at DESC LIMIT ?", (limit,))
            return [Campaign.model_validate_json(r["data_json"]) for r in cur.fetchall()]


db = CampaignDatabase()
