from common.config.settings import Settings
from common.consumers.kafka_consumer import KafkaConsumer
from processor.processor_service import ProcessorService


def execute():
    settings = Settings()

    consumer = KafkaConsumer(
        kafka_bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.CONSUMER_GROUP_ID,
        topic=settings.COINGECKO_KAFKA_TOPIC,
    )

    processor_service = ProcessorService(
        settings=settings,
        kafka_consumer=consumer,
    )

    processor_service.run()


if __name__ == "__main__":
    execute()
