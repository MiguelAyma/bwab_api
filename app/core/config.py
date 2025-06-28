from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()
DB_URL= os.getenv("DB_URL", "sqlite:///./test.db")
class Settings(BaseSettings):
    ALLOW_ORIGINS: list[str] = ["*"]
    DB_URL: str = DB_URL 
    class Config:
        env_file = "/.env"
    
settings = Settings()

