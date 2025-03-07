import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
from sqlalchemy.orm import Session

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # API Settings
    marketstack_api_key: str
    api_rate_limit: int = 5  # requests per second
    
    # Database Settings
    database_url: str
    db: Optional[Session] = None
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Cache Settings
    cache_ttl: int = 3600  # Default cache TTL in seconds
    
    # Application Settings
    tracked_stocks: List[str] = []  # List of stock symbols to track
    update_interval: int = 300  # 5 minutes in seconds
    
    # IPO Settings
    ipo_check_interval: int = 86400  # 24 hours in seconds
    
    class Config:
        env_file = os.path.join(BACKEND_DIR, ".env")

@lru_cache()
def get_settings() -> Settings:
    return Settings() 