# pylint: disable=protected-access
import signal
import socket

import structlog
from confluent_kafka import Consumer, KafkaError, KafkaException
from structlog.typing import FilteringBoundLogger

default_logger = structlog.get_logger()


class KafkaConsumer:
    def __init__(
        self,
        kafka_bootstrap_servers: str,
        group_id: str,
        topic: str,
        logger: FilteringBoundLogger = default_logger,
    ):
        conf = {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "client.id": socket.gethostname(),
        }
        self.consumer = Consumer(conf)
        self.topic = topic
        self.logger = logger
        self._running = True

    def _shutdown_handler(self, signum, _):
        self.logger.info(
            "KafkaConsumer: Shutdown signal received",
            signal_number=signum,
        )
        self.stop()

    def setup_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        self.logger.info("KafkaConsumer: Signal handlers registered")

    def consume_messages(self, message_handler):
        try:
            self.consumer.subscribe([self.topic])
            self.logger.info(f"Subscribed to topic: {self.topic}")

            while self._running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.logger.info(
                            f"End of partition reached "
                            f"{msg.topic()}[{msg.partition()}] at offset "
                            f"{msg.offset()}"
                        )
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    self.logger.info(f"Message received from topic {msg.topic()}")
                    message_handler(msg.value().decode("utf-8"))
        finally:
            self.logger.info("KafkaConsumer: Closing consumer")
            self.consumer.close()

    def stop(self):
        self.logger.info("KafkaConsumer: Stopping consumer")
        self._running = False
