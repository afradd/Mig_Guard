# Reads environment variables cleanly
import os
from dotenv import load_dotenv

class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "8"))

settings = Settings()