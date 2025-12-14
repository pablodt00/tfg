# pylint: disable=redefined-outer-name, protected-access

import json
from unittest.mock import Mock

import pytest

from processor.processor_service import ProcessorService


@pytest.fixture
def service_components():
    mock_settings = Mock()
    mock_kafka_consumer = Mock()
    mock_logger = Mock()
    service = ProcessorService(
        settings=mock_settings,
        kafka_consumer=mock_kafka_consumer,
        logger=mock_logger,
    )
    return service, mock_kafka_consumer, mock_logger


def test_run(service_components):
    service, mock_kafka_consumer, mock_logger = service_components
    service.run()
    mock_logger.info.assert_called_with("ProcessorService: Running")
    mock_kafka_consumer.consume_messages.assert_called_once_with(
        service._handle_message
    )


def test_handle_message_valid_json(service_components):
    service, _, mock_logger = service_components
    valid_data = {"key": "value"}
    message = json.dumps(valid_data)

    service._handle_message(message)

    mock_logger.info.assert_any_call("Received Kafka message", message=message)
    mock_logger.info.assert_any_call("Processing message", data=valid_data)
    mock_logger.error.assert_not_called()


def test_handle_message_invalid_json(service_components):
    service, _, mock_logger = service_components
    message = "not a valid json"

    service._handle_message(message)

    mock_logger.info.assert_any_call("Received Kafka message", message=message)
    mock_logger.error.assert_called_once_with(
        "Failed to decode message", message=message
    )
