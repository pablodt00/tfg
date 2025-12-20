from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    COINGECKO_API_KEY: str = Field(
        alias="COINGECKO_API_KEY",
        description="CoinGecko API key for authentication.",
    )

    COINGECKO_BASE_URL: str = Field(
        alias="COINGECKO_BASE_URL",
        description="Base URL for CoinGecko API requests.",
    )

    COINGECKO_TIMEOUT: int = Field(
        alias="COINGECKO_TIMEOUT", description="Timeout for CoinGecko API requests."
    )

    # Heartbeat settings
    HEARTBEAT_FILE: str = Field(alias="HEARTBEAT_FILE")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(alias="KAFKA_BOOTSTRAP_SERVERS")

    COINGECKO_KAFKA_TOPIC: str = Field(alias="COINGECKO_KAFKA_TOPIC")

    # Consumers
    CONSUMER_GROUP_ID: str = Field(alias="CONSUMER_GROUP_ID")

    # Database
    DB_HOST: str = Field(alias="DB_HOST")

    DB_PORT: int = Field(alias="DB_PORT", default=5432)

    DB_USER: str = Field(alias="DB_USER")

    DB_PASSWORD: str = Field(alias="DB_PASSWORD")

    DB_NAME: str = Field(alias="DB_NAME")

    @property
    def db_uri_as_string(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
