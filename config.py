"""Configuration management for Backpack CLI Bot."""

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
    WS_URL: str = os.getenv("WS_URL", "wss://ws.backpack.exchange")

    # Trading Configuration
    DEFAULT_SYMBOL: str = os.getenv("DEFAULT_SYMBOL", "SOL_USDC")
    DEFAULT_LEVERAGE: int = int(os.getenv("DEFAULT_LEVERAGE", "1"))
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "1000"))
    RISK_PERCENTAGE: float = float(os.getenv("RISK_PERCENTAGE", "1.0"))

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
