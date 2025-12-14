import socket

import structlog
from confluent_kafka import Producer
from pydantic import BaseModel
from structlog.typing import FilteringBoundLogger

default_logger = structlog.get_logger()


class KafkaProducer:
    def __init__(
        self,
        kafka_bootstrap_servers: str,
        topic: str,
        logger: FilteringBoundLogger = default_logger,
    ):
        conf = {
            "bootstrap.servers": kafka_bootstrap_servers,
            "client.id": socket.gethostname(),
        }
        self.producer = Producer(conf)
        self.topic = topic
        self.logger = logger

    @staticmethod
    def _delivery_report(err, msg):
        if err is not None:
            default_logger.info(f"Message delivery failed: {err}")
        else:
            default_logger.info(
                f"Message produced to {msg.topic()} [{msg.partition()}]"
            )

    def produce_message(self, message: BaseModel):
        self.producer.produce(
            topic=self.topic,
            value=message.model_dump_json().encode("utf-8"),
            callback=self._delivery_report,
        )
        self.producer.flush()
