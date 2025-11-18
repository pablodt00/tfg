from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    COINGECKO_API_KEY: str = Field(
        default="CG-HJ1MQ4HXvhWUz9J7aRQgbUUw",
        description="CoinGecko API key for authentication.",
    )

    COINGECKO_BASE_URL: str = Field(
        default="https://api.coingecko.com/api/v3",
        description="Base URL for CoinGecko API requests.",
    )

    COINGECKO_TIMEOUT: int = Field(
        default=10, description="Timeout for CoinGecko API requests."
    )
