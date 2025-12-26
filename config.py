"""Configuration management for the Job Agent Bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for the bot."""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Groq LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Jooble Job API
    JOOBLE_API_KEY: str = os.getenv("JOOBLE_API_KEY", "")
    JOOBLE_API_URL: str = "https://jooble.org/api/"
    
    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    GOOGLE_SHEET_URL: str = os.getenv("GOOGLE_SHEET_URL", "")
    
    # Google Custom Search (scrapping /more)
    GOOGLE_SEARCH_KEY: str = os.getenv("GOOGLE_SEARCH_KEY", "")
    GOOGLE_SEARCH_CX: str = os.getenv("GOOGLE_SEARCH_CX", "")
    
    # OpenRouter API (for query expansion)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Default search preferences
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "remote")
    DEFAULT_SEARCH_RADIUS: int = int(os.getenv("DEFAULT_SEARCH_RADIUS", "50"))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration values are set.
        
        Returns:
            List of missing configuration keys.
        """
        missing = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not cls.JOOBLE_API_KEY:
            missing.append("JOOBLE_API_KEY")
        if not cls.GOOGLE_SERVICE_ACCOUNT_FILE:
            missing.append("GOOGLE_SERVICE_ACCOUNT_FILE")
        if not cls.GOOGLE_SHEET_URL:
            missing.append("GOOGLE_SHEET_URL")
            
        return missing
    
    @classmethod
    def ensure_dirs(cls) -> None:
        """Ensure required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
