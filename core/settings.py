
from pydantic import BaseModel
from decouple import config


class Settings(BaseModel):
    PROJECT_TITLE: str = "FastAPI Auth"
    PROJECT_VERSION: str = "1.0.0"

    USE_SQLITE_DB: str = config("USE_SQLITE_DB")

    POSTGRES_USER: str = config("POSTGRES_USER")
    POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = config("POSTGRES_PORT")
    POSTGRES_DB: str = config("POSTGRES_DB")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_FROM: str = config("MAIL_FROM")
    MAIL_PORT: str = config("MAIL_PORT")
    MAIL_SERVER: str = config("MAIL_SERVER")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SECRET_KEY: str = config("SECRET")
    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRY_SECONDS: int = 900
    REFRESH_TOKEN_EXPIRY_DAYS: int = 30
    EMAIL_TOKEN_EXPIRY_MINUTES: int = 30
    RESET_TOKEN_EXPIRY_MINUTES: int = 30


settings = Settings()
