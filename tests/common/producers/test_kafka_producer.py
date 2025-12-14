# pylint: disable=protected-access, unused-argument
from unittest.mock import MagicMock, patch

from pydantic import BaseModel

from common.producers.kafka_producer import KafkaProducer


class DummyModel(BaseModel):
    field: str


@patch("socket.gethostname", return_value="test-host")
@patch("common.producers.kafka_producer.Producer")
def test_kafka_producer_init(mock_producer_cls, mock_gethostname):
    bootstrap_servers = "kafka:9092"
    topic = "test-topic"
    KafkaProducer(kafka_bootstrap_servers=bootstrap_servers, topic=topic)

    expected_conf = {"bootstrap.servers": bootstrap_servers, "client.id": "test-host"}
    mock_producer_cls.assert_called_once_with(expected_conf)


@patch("socket.gethostname", return_value="test-host")
@patch("common.producers.kafka_producer.Producer")
def test_produce_message(mock_producer_cls, mock_gethostname):
    mock_producer_instance = MagicMock()
    mock_producer_cls.return_value = mock_producer_instance

    topic = "my-topic"
    producer = KafkaProducer(kafka_bootstrap_servers="kafka:9092", topic=topic)

    message = DummyModel(field="my-message")
    producer.produce_message(message)

    mock_producer_instance.produce.assert_called_once_with(
        topic=topic,
        value=message.model_dump_json().encode("utf-8"),
        callback=producer._delivery_report,
    )
    mock_producer_instance.flush.assert_called_once()
