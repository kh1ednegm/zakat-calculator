from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""

    APP_NAME: str = "حاسبة الزكاة"
    ENV: str = "development"
    SECRET_KEY: str = "change-me-to-a-long-random-string"
    DATABASE_URL: str = "sqlite:///./zakat.db"
    SESSION_COOKIE: str = "zakat_session"
    SESSION_MAX_AGE: int = 60 * 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
