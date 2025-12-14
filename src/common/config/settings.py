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
