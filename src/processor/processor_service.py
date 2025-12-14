import json

import structlog
from structlog.typing import FilteringBoundLogger

from common.config.settings import Settings
from common.consumers.kafka_consumer import KafkaConsumer

default_logger = structlog.get_logger()


class ProcessorService:
    def __init__(
        self,
        settings: Settings,
        kafka_consumer: KafkaConsumer,
        logger: FilteringBoundLogger = default_logger,
    ):
        self.settings = settings
        self.kafka_consumer = kafka_consumer
        self.logger = logger

    def _handle_message(self, message: str):
        self.logger.info("Received Kafka message", message=message)

        try:
            data = json.loads(message)
            self.logger.info("Processing message", data=data)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode message", message=message)

    def run(self):
        self.logger.info("ProcessorService: Running")
        self.kafka_consumer.consume_messages(self._handle_message)
