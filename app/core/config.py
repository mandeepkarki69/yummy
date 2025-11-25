from pydantic_settings import BaseSettings  # updated import

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://mandeep:kxyneRmTzPVDSMzw19efk0GpmZ7Dkbmf@dpg-d4im8sa4d50c73d6rnl0-a.singapore-postgres.render.com/yummy_db_z8q4?sslmode=require"
    APP_NAME: str = "Yummy API"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
