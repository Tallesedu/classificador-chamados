from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM
    llm_provider: str = Field(default="ollama")   # "ollama" ou "groq"
    llm_base_url: str = Field(default="http://localhost:11434")
    llm_model: str = Field(default="llama3.2")
    llm_timeout: int = Field(default=60)

    # Groq (usado apenas quando llm_provider="groq")
    groq_api_key: str = Field(default="")

    # Segurança
    api_key: str = Field(default="dev-key-insecure")

    # App
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")


settings = Settings()
