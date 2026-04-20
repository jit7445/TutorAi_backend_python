import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    FASTAPI_PORT: int = 8000
    INTERNAL_API_SECRET: str = "super-secret-shared-key-change-this"
    UPSTASH_REDIS_URL: str = "redis://localhost:6379"
    GOOGLE_SERVICE_ACCOUNT_JSON: str = "service_account.json"
    GDRIVE_ROOT_FOLDER_ID: str = "your_folder_id"
    gpt_api_key: str = ""
    Gemini_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
