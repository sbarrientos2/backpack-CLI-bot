"""Configuration management for Backpack CLI Bot.

SECURITY WARNINGS:
- Never commit your .env file to version control
- Never share your API keys with anyone
- Rotate your API keys regularly (monthly recommended)
- Use read-only API keys if you only need to view data
- Set IP restrictions on your API keys when possible
- Monitor your API key usage for suspicious activity
"""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Application configuration."""

    # API Credentials
    BACKPACK_API_KEY: str = os.getenv("BACKPACK_API_KEY", "")
    BACKPACK_API_SECRET: str = os.getenv("BACKPACK_API_SECRET", "")

    # API Endpoints
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.backpack.exchange")

    # Trading Configuration
    DEFAULT_SYMBOL: str = os.getenv("DEFAULT_SYMBOL", "SOL_USDC")

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is set."""
        if not cls.BACKPACK_API_KEY or not cls.BACKPACK_API_SECRET:
            return False
        return True

    @classmethod
    def get_api_credentials(cls) -> tuple[str, str]:
        """Get API credentials as tuple."""
        return cls.BACKPACK_API_KEY, cls.BACKPACK_API_SECRET


config = Config()
