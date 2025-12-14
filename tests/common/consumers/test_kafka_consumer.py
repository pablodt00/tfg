# pylint: disable=redefined-outer-name, protected-access
from unittest.mock import MagicMock, patch

import pytest
from confluent_kafka import KafkaError, KafkaException

from common.consumers.kafka_consumer import KafkaConsumer


@pytest.fixture
def mock_consumer_class():
    with patch("common.consumers.kafka_consumer.Consumer") as mock_class:
        yield mock_class


@pytest.fixture
def mock_consumer(mock_consumer_class):
    mock_instance = MagicMock()
    mock_consumer_class.return_value = mock_instance
    return mock_instance


@pytest.fixture
def mock_socket():
    with patch("socket.gethostname", return_value="test-host") as mock_socket_patch:
        yield mock_socket_patch


def test_kafka_consumer_init(mock_consumer_class, mock_consumer, mock_socket):
    kafka_consumer = KafkaConsumer(
        kafka_bootstrap_servers="localhost:9092",
        group_id="test-group",
        topic="test-topic",
    )

    expected_conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "test-group",
        "auto.offset.reset": "earliest",
        "client.id": "test-host",
    }

    mock_consumer_class.assert_called_once_with(expected_conf)
    assert kafka_consumer.consumer == mock_consumer
    assert kafka_consumer.topic == "test-topic"
    assert kafka_consumer._running is True
    mock_socket.assert_called_once()


def test_consume_messages_success(mock_consumer):
    kafka_consumer = KafkaConsumer("localhost:9092", "test-group", "test-topic")
    mock_message = MagicMock()
    mock_message.error.return_value = None
    mock_message.value.return_value = b'{"key": "value"}'
    mock_message.topic.return_value = "test-topic"

    mock_consumer.poll.side_effect = [mock_message, StopIteration]

    message_handler = MagicMock()

    with pytest.raises(StopIteration):
        kafka_consumer.consume_messages(message_handler)

    mock_consumer.subscribe.assert_called_once_with(["test-topic"])
    assert mock_consumer.poll.call_count == 2
    message_handler.assert_called_once_with('{"key": "value"}')
    mock_consumer.close.assert_called_once()


def test_consume_messages_partition_eof(mock_consumer):
    kafka_consumer = KafkaConsumer("localhost:9092", "test-group", "test-topic")
    mock_error = MagicMock()
    mock_error.code.return_value = KafkaError._PARTITION_EOF
    mock_message = MagicMock()
    mock_message.error.return_value = mock_error
    mock_message.topic.return_value = "test-topic"
    mock_message.partition.return_value = 1
    mock_message.offset.return_value = 100

    mock_consumer.poll.side_effect = [mock_message, None]
    kafka_consumer.stop()

    message_handler = MagicMock()
    kafka_consumer.consume_messages(message_handler)

    message_handler.assert_not_called()
    mock_consumer.close.assert_called_once()


def test_consume_messages_kafka_exception(mock_consumer):
    kafka_consumer = KafkaConsumer("localhost:9092", "test-group", "test-topic")
    mock_error = MagicMock()
    mock_error.code.return_value = KafkaError.UNKNOWN_TOPIC_OR_PART
    mock_message = MagicMock()
    mock_message.error.return_value = mock_error

    mock_consumer.poll.return_value = mock_message

    with pytest.raises(KafkaException):
        kafka_consumer.consume_messages(MagicMock())

    mock_consumer.close.assert_called_once()


def test_stop():
    kafka_consumer = KafkaConsumer("localhost:9092", "test-group", "test-topic")
    assert kafka_consumer._running is True
    kafka_consumer.stop()
    assert kafka_consumer._running is False
