# from unittest.mock import MagicMock, patch
#
# from processor.processor_daemon import execute
#
#
# @patch("processor.processor_daemon.ProcessorService")
# @patch("processor.processor_daemon.KafkaConsumer")
# @patch("processor.processor_daemon.Settings")
# def test_execute(
#     mock_settings_cls, mock_kafka_consumer_cls, mock_processor_service_cls
# ):
#     mock_settings = MagicMock()
#     mock_settings.KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
#     mock_settings.CONSUMER_GROUP_ID = "test-group"
#     mock_settings.COINGECKO_KAFKA_TOPIC = "test-topic"
#     mock_settings_cls.return_value = mock_settings
#
#     mock_consumer = MagicMock()
#     mock_kafka_consumer_cls.return_value = mock_consumer
#
#     mock_service = MagicMock()
#     mock_processor_service_cls.return_value = mock_service
#
#     execute()
#
#     mock_settings_cls.assert_called_once()
#
#     mock_kafka_consumer_cls.assert_called_once_with(
#         kafka_bootstrap_servers=mock_settings.KAFKA_BOOTSTRAP_SERVERS,
#         group_id=mock_settings.CONSUMER_GROUP_ID,
#         topic=mock_settings.COINGECKO_KAFKA_TOPIC,
#     )
#
#     mock_processor_service_cls.assert_called_once_with(
#         settings=mock_settings,
#         kafka_consumer=mock_consumer,
#     )
#
#     mock_service.run.assert_called_once()
