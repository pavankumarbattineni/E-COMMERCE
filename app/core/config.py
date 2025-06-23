from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
import os

# Load .env values
load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    allowed_origins: str  # will now be read from .env as a JSON array

    @property
    def origins(self):
        return self.allowed_origins

settings = Settings()
