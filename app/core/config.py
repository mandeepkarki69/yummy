from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment.

    Secrets like DATABASE_URL and JWT_SECRET_KEY should be rotated
    outside of code (change in your deployment environment) and this
    class will pick up new values on restart.
    """
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # default: 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # default: 7 days
    RATE_LIMIT_REQUESTS: int = 100  # max requests per window per client
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # window size in seconds
    DATABASE_SSL: bool = True
    APP_NAME: str = "Yummy API"
    DEBUG: bool = True
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    USE_S3_UPLOADS: bool = False
    AWS_S3_BUCKET: str | None = None
    AWS_S3_REGION: str | None = None
    AWS_S3_ENDPOINT_URL: str | None = None
    AWS_S3_PUBLIC_URL_PREFIX: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
