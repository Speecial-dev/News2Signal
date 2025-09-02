from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os, secrets, logging

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev_secret")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


settings = Settings()

if not settings.JWT_SECRET:
    # DEV fallback: prod’da bunu istemezsin, .env şart
    settings.JWT_SECRET = secrets.token_urlsafe(64)
    logging.warning("JWT_SECRET env yok. Geçici bir secret üretildi (sadece geliştirme için).")