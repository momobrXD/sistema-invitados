import os
from dotenv import load_dotenv

load_dotenv()  # carga backend/.env automáticamente


def _normalize_database_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


DATABASE_URL = (
    _normalize_database_url(os.environ.get("DATABASE_URL"))
    or "sqlite:///./local.db"
)

SECRET_KEY = os.environ.get("SECRET_KEY", "mcc_sistema_2026_pro_secure")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
ALGORITHM = "HS256"
