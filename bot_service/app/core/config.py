from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "bot-service"
    ENV: str = "local"

    TELEGRAM_BOT_TOKEN: str = ""

    JWT_SECRET: str
    JWT_ALG: str = "HS256"

    REDIS_URL: str
    RABBITMQ_URL: str

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str
    OPENROUTER_SITE_URL: str = ""
    OPENROUTER_APP_NAME: str = "bot-service"


settings = Settings()
