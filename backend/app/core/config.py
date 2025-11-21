from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./venancio.db"

    # Scraper
    RECLAME_AQUI_COMPANY_URL: str = "https://www.reclameaqui.com.br/empresa/drogaria-venancio-site-e-televendas"
    SCRAPER_DELAY_MIN: int = 2
    SCRAPER_DELAY_MAX: int = 5
    SCRAPER_MAX_PAGES: int = 300
    SCRAPER_POLLING_INTERVAL_HOURS: int = 6

    # API
    API_TITLE: str = "Venâncio RPA API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3003

    # Google Gemini AI
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


settings = Settings()
