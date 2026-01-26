from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    DEFAULT_MODEL: str = "IlyaGusev/rut5_base_sum_gazeta"
    MAX_SOURCE_TOKENS: int = 600

    DEVICE: Optional[str] = None # Will auto-detect cuda/cpu if None

    NO_REPEAT_NGRAM_SIZE: int = 4
    MAX_NEW_TOKENS: int = 200 # Maximum length of generated summary
    MIN_LENGTH: int = 2 # Minimum length of generated summary
    NUM_BEAMS: int = 5
    LENGTH_PENALTY: float = 1.0
    EARLY_STOPPING: bool = True # Stop when EOS token is generated

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
