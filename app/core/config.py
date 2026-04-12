from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Sample FastAPI"
    debug: bool = False
    database_url: str = "sqlite:///./dev.db"

    class Config:
        env_file = ".env"

settings = Settings()
