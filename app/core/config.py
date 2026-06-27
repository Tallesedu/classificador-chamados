from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    llm_provider: str = Field(default="ollama")
    llm_base_url: str = Field(default="http://localhost:11434")
    llm_model: str = Field(default="llama3.1:8b")
    llm_timeout: int = Field(default=60)

    groq_api_key: str = Field(default="")

    jwt_secret: str = Field(default="temp")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_minutes: int = Field(default=60, ge=1, le=1440)

    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")


settings = Settings()
