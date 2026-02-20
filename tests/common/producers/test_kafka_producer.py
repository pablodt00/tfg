# pylint: disable=protected-access
from unittest.mock import MagicMock, patch

from pydantic import BaseModel

from common.producers.kafka_producer import KafkaProducer


class SampleModel(BaseModel):
    value: str


@patch("socket.gethostname", return_value="test-host")
@patch("common.producers.kafka_producer.Producer")
def test_init_creates_producer(mock_producer_cls, _):
    KafkaProducer(kafka_bootstrap_servers="kafka:9092", topic="test-topic")
    mock_producer_cls.assert_called_once_with(
        {"bootstrap.servers": "kafka:9092", "client.id": "test-host"}
    )


@patch("socket.gethostname", return_value="test-host")
@patch("common.producers.kafka_producer.Producer")
def test_produce_message_calls_produce_and_flush(mock_producer_cls, _):
    mock_instance = MagicMock()
    mock_producer_cls.return_value = mock_instance

    producer = KafkaProducer(kafka_bootstrap_servers="kafka:9092", topic="my-topic")
    msg = SampleModel(value="hello")
    producer.produce_message(msg)

    mock_instance.produce.assert_called_once_with(
        topic="my-topic",
        value=msg.model_dump_json().encode("utf-8"),
        callback=KafkaProducer._delivery_report,
    )
    mock_instance.flush.assert_called_once()


@patch("common.producers.kafka_producer.Producer")
def test_delivery_report_no_error(_):
    KafkaProducer._delivery_report(None, MagicMock())


@patch("common.producers.kafka_producer.Producer")
def test_delivery_report_with_error(_):
    KafkaProducer._delivery_report("some error", MagicMock())
