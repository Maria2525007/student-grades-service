from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/grades_db"

    model_config = {"env_file": ".env"}


settings = Settings()
