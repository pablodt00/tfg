# pylint: disable=duplicate-code
from common.config.settings import Settings
from common.consumers.kafka_consumer import KafkaConsumer
from common.database import make_engine, make_session_factory
from common.database.repositories.alert_repository import AlertRepository
from common.database.repositories.coin_repository import CoinRepository
from processor.processor_service import ProcessorService


def execute():
    settings = Settings()

    consumer = KafkaConsumer(
        kafka_bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.CONSUMER_GROUP_ID,
        topic=settings.COINGECKO_KAFKA_TOPIC,
    )

    consumer.setup_signal_handlers()

    engine = make_engine(
        db_uri=settings.db_uri_as_string,
    )

    session_factory = make_session_factory(
        engine=engine,
    )

    coin_repository = CoinRepository()

    alert_repository = AlertRepository()

    processor_service = ProcessorService(
        settings=settings,
        kafka_consumer=consumer,
        coin_repository=coin_repository,
        alert_repository=alert_repository,
        session_factory=session_factory,
    )

    processor_service.run()


if __name__ == "__main__":
    execute()
