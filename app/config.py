from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Hostel Management System"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hostel_db"
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    FIREBASE_CREDENTIALS: str | None = None
    FIREBASE_STORAGE_BUCKET: str | None = None

    MPESA_CONSUMER_KEY: str | None = None
    MPESA_CONSUMER_SECRET: str | None = None
    MPESA_SHORTCODE: str | None = None
    MPESA_PASSKEY: str | None = None
    MPESA_CALLBACK_URL: str | None = None
    MPESA_ENVIRONMENT: str = "sandbox"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
