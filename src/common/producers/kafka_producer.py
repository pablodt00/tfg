import socket

from confluent_kafka import Producer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": socket.gethostname(),
        }
        self.producer = Producer(conf)

    @staticmethod
    def _delivery_report(err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message produced to {msg.topic()} [{msg.partition()}]")

    def produce_message(self, topic: str, message: str):
        self.producer.produce(
            topic, value=message.encode("utf-8"), callback=self._delivery_report
        )
        self.producer.flush()
