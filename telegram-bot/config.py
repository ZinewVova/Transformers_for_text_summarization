from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    FASTAPI_URL: str = "http://localhost:8000"
    FASTAPI_TIMEOUT: int = 60
    MIN_MESSAGE_LENGTH: int = 50
    MAX_MESSAGE_LENGTH: int = 4000

    class Config:
        # Use absolute path to .env file in telegram-bot directory
        env_file = Path(__file__).parent / ".env"
        case_sensitive = True


settings = Settings()
