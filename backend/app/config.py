# Reads all environment variables for the backend in one place.
# Import `settings` anywhere in the app — never read os.getenv() directly in routes.
import os
from pathlib import Path
from dotenv import load_dotenv

# Always locate the backend/.env file regardless of current working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv()


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "8"))
    primary_llm_api_key: str = os.getenv("PRIMARY_LLM_API_KEY", "")
    primary_llm_model: str = os.getenv(
        "PRIMARY_LLM_MODEL",
        "gemini-2.5-flash",
    )
    fallback_llm_api_key: str = os.getenv("FALLBACK_LLM_API_KEY", "")
    fallback_llm_model: str = os.getenv(
        "FALLBACK_LLM_MODEL",
        "gemini-2.5-flash-lite",
    )

settings = Settings()