import os
from pydantic_settings import BaseSettings
from functools import lru_cache

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # API Settings
    MARKETSTACK_API_KEY: str
    MARKETSTACK_BASE_URL: str = "http://api.marketstack.com/v1"
    
    # Database Settings
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_SCHEMA: str = "stocksight"  # Default schema name
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?options=-csearch_path%3D{self.DB_SCHEMA}"
    
    # API Rate Limiting
    API_RATE_LIMIT: int = 100  # requests per minute
    
    class Config:
        env_file = os.path.join(BACKEND_DIR, ".env")

@lru_cache()
def get_settings():
    return Settings() 