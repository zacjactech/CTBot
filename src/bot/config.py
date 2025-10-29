import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    api_key: str = Field(..., alias="BINANCE_API_KEY")
    api_secret: str = Field(..., alias="BINANCE_API_SECRET")
    base_url: str = Field(
        default="https://testnet.binancefuture.com", alias="BINANCE_FUTURES_BASE_URL"
    )
    recv_window: int = 5000
    default_symbol: str = "BTCUSDT"


def get_settings() -> Settings:
    return Settings()

settings = get_settings()
