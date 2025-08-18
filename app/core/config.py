from __future__ import annotations
import yaml
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional


class AppSettings(BaseModel):
    name: str = "EpicGames API"
    debug: bool = False


class DBSettings(BaseModel):
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class ScraperSettings(BaseModel):
    base_url: str
    browse_path: str
    concurrency: int = 5
    request_timeout: int = 20
    delay_between_requests_ms: int = 300
    user_agents: list[str] = []
    smart_dns: Optional[List[str]] = None


class Settings(BaseModel):
    app: AppSettings
    database: DBSettings
    scraper: ScraperSettings


# Fix for Pydantic v2
Settings.model_rebuild()


def load_settings(config_path: str | Path = "config.yaml") -> Settings:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Settings(**data)


settings = load_settings()
