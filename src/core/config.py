from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    DB_HOST: str

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()
