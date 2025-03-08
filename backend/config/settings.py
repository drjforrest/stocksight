import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
from sqlalchemy.orm import Session

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # API Settings
    marketstack_api_key: str = ""  # type: ignore[reportGeneralTypeIssues]
    serper_api_key: str = ""  # type: ignore[reportGeneralTypeIssues]
    api_rate_limit: int = 5  # requests per second
    
    # Database Settings
    database_url: str = ""  # type: ignore[reportGeneralTypeIssues]
    db: Optional[Session] = None
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    @property
    def redis_url(self) -> str:
        """Constructs Redis URL from individual settings"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # Cache Settings
    cache_ttl: int = 3600  # Default cache TTL in seconds
    
    # Application Settings
    tracked_stocks: List[str] = []  # List of stock symbols to track
    update_interval: int = 300  # 5 minutes in seconds
    
    # IPO Settings
    ipo_check_interval: int = 86400  # 24 hours in seconds

    # JWT Settings
    jwt_secret_key: str = "your-secret-key-here"  # Should be set in .env
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Environment Settings
    pythonpath: Optional[str] = None
    virtual_env: Optional[str] = None
    
    class Config:
        env_file = os.path.join(BACKEND_DIR, ".env")
        env_required = ["marketstack_api_key", "serper_api_key", "database_url"]

@lru_cache()
def get_settings() -> Settings:
    return Settings() 