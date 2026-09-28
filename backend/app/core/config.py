from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "Kirana AI Backend"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kirana_db"

    # JWT Authentication
    JWT_SECRET_KEY: str = "dev_secret_key_change_in_production_1234567890"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # External Integrations
    HINDSIGHT_BASE_URL: str = "https://api.hindsight.ai/v1"
    HINDSIGHT_API_URL: str = "https://api.hindsight.ai/v1"
    HINDSIGHT_API_KEY: str = "mock_hindsight_key"

    GEMINI_API_KEY: str = "mock_gemini_key"
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Sarvam AI Speech-to-Text (Saaras) & Text-to-Speech (Bulbul)
    SARVAM_API_KEY: str = "mock_sarvam_key"
    SARVAM_BASE_URL: str = "https://api.sarvam.ai"

    WEATHER_API_KEY: str = "mock_weather_key"
    WEATHER_API_URL: str = "https://api.weather.com/v1"

    AGMARKNET_API_URL: str = "https://agmarknet.gov.in/api/v1"
    AGMARKNET_API_KEY: str = "mock_agmarknet_key"

    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_ACCESS_TOKEN: str = "mock_whatsapp_token"
    WHATSAPP_PHONE_NUMBER_ID: str = "mock_whatsapp_phone_id"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
