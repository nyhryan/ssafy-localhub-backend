from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_file_name: str = "database.db"
    db_url: str = f"sqlite:///{db_file_name}"
    db_connect_args: dict = {"check_same_thread": False}
    openai_api_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()