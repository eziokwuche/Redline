from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./ats.db'
    llm_provider: str = 'groq'
    groq_api_key: str = ''
    groq_model: str = 'openai/gpt-oss-120b'
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.6-flash'
    ollama_base_url: str = 'http://localhost:11434'
    ollama_model: str = 'llama3.2'
    max_upload_mb: int = 10
    upload_dir: str = 'storage/uploads'
    environment: str = 'development'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
