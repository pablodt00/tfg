from common.config.settings import Settings
from common.daemons.heartbeat_handler import make_heartbeat_handler
from common.producers.kafka_producer import KafkaProducer
from gateway.coingecko_base_daemon import CoinGeckoBaseDaemon
from gateway.coingecko_controller import CoinGeckoAPIController
from gateway.coingecko_service import CoinGeckoAPIService


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

    coingecko_api_controller = CoinGeckoAPIController(
        service=coingecko_api_service,
    )

    coingecko_base_daemon = CoinGeckoBaseDaemon(
        controller=coingecko_api_controller,
        heartbeat_handler=make_heartbeat_handler(settings=settings),
    )

    coingecko_base_daemon.start()


if __name__ == "__main__":
    execute()
