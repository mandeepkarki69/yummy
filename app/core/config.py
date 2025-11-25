from pydantic_settings import BaseSettings  # updated import

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1234567890@localhost:5432/yummy_db"
    APP_NAME: str = "Yummy API"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
