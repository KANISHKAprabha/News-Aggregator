from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    env_name: str ="Local"
    base_url : str = "http://localhost:8000"
    db_url : str = "sqlite:///./news_aggregator.db"
    class Config:
        env_file = ".env"
        

@lru_cache()
def get_settings()-> Settings:
    settings =Settings()
    print(f"Environment: {settings.base_url}")
    return settings
