# pylint: disable=protected-access, unused-argument
from unittest.mock import MagicMock, patch

from common.producers.kafka_producer import KafkaProducer


@patch("socket.gethostname", return_value="test-host")
@patch("common.producers.kafka_producer.Producer")
def test_kafka_producer_init(mock_producer_cls, mock_gethostname):
    bootstrap_servers = "kafka:9092"
    KafkaProducer(bootstrap_servers=bootstrap_servers)

    expected_conf = {"bootstrap.servers": bootstrap_servers, "client.id": "test-host"}
    mock_producer_cls.assert_called_once_with(expected_conf)


@patch("socket.gethostname", return_value="test-host")
@patch("common.producers.kafka_producer.Producer")
def test_produce_message(mock_producer_cls, mock_gethostname):
    mock_producer_instance = MagicMock()
    mock_producer_cls.return_value = mock_producer_instance

    producer = KafkaProducer(bootstrap_servers="kafka:9092")

    topic = "my-topic"
    message = "my-message"
    producer.produce_message(topic, message)

    mock_producer_instance.produce.assert_called_once_with(
        topic, value=message.encode("utf-8"), callback=producer._delivery_report
    )
    mock_producer_instance.flush.assert_called_once()
