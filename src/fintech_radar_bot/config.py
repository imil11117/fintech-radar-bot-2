"""
Configuration management for the Fintech Radar Bot.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the bot."""
    
    # Telegram Bot Configuration
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.example.com")
    API_KEY: Optional[str] = os.getenv("API_KEY")
    
    # Scheduling Configuration
    POST_TIME: str = os.getenv("POST_TIME", "09:00")  # Daily post time (24h format)
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")
    
    # Data Sources Configuration
    NEWS_SOURCES: list = os.getenv("NEWS_SOURCES", "").split(",") if os.getenv("NEWS_SOURCES") else []
    MAX_ARTICLES_PER_UPDATE: int = int(os.getenv("MAX_ARTICLES_PER_UPDATE", "5"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required_fields = ["BOT_TOKEN", "CHANNEL_ID"]
        
        for field in required_fields:
            if not getattr(cls, field):
                raise ValueError(f"Required configuration field '{field}' is not set")
        
        return True


# Global configuration instance
config = Config()
