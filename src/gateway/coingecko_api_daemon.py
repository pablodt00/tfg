from common.config.settings import Settings
from common.producers.kafka_producer import KafkaProducer
from gateway.coingecko_service import CoinGeckoAPIService
from gateway.endpoints.app import build_coingecko_api_daemon


def execute():

    settings = Settings()

    kafka_producer = KafkaProducer(
        kafka_bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=settings.COINGECKO_KAFKA_TOPIC,
    )

    coingecko_api_service = CoinGeckoAPIService(
        settings=settings,
        kafka_producer=kafka_producer,
    )

    return build_coingecko_api_daemon(
        coingecko_api_service=coingecko_api_service,
    )


if __name__ == "__main__":
    import os

    import uvicorn

    app_name = os.path.basename(__file__).replace(".py", "")
    uvicorn.run(
        app=f"gateway.{app_name}:execute",
        host="0.0.0.0",
        port=8000,
        workers=1,
        factory=True,
    )
