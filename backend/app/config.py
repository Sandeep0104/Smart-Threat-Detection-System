"""
AI Security Analyst - Configuration
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # Paths
    UPLOAD_DIR: str = "./uploads"
    VECTOR_STORE_DIR: str = "./vector_store"
    REPORTS_DIR: str = "./reports"
    MAX_FILE_SIZE_MB: int = 50

    # Threat Detection
    BRUTE_FORCE_THRESHOLD: int = 5
    BRUTE_FORCE_WINDOW_MINUTES: int = 10
    PORT_SCAN_THRESHOLD: int = 10
    UNUSUAL_HOUR_START: int = 0
    UNUSUAL_HOUR_END: int = 5

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
