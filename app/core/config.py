from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

class Settings(BaseSettings):
    allowed_origins: List[str]
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    database_url: str = os.getenv("DATABASE_URL")

    @property
    def origins(self) -> List[str]:
        return self.allowed_origins

settings = Settings()
