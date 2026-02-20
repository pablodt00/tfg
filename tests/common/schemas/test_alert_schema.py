from datetime import datetime

from common.schemas.alert import Alert, AlertConditionEnum


def test_alert_condition_enum_values():
    assert AlertConditionEnum.GREATER_THAN_OR_EQUAL == "GREATER_THAN_OR_EQUAL"
    assert AlertConditionEnum.LESS_THAN_OR_EQUAL == "LESS_THAN_OR_EQUAL"
    assert str(AlertConditionEnum.GREATER_THAN_OR_EQUAL) == "GREATER_THAN_OR_EQUAL"


def test_alert_from_alert_factory():
    alert = Alert.from_alert(
        coin="btc",
        condition=AlertConditionEnum.GREATER_THAN_OR_EQUAL,
        user_email="test@example.com",
        amount=50000.0,
    )
    assert alert.coin == "btc"
    assert alert.condition == AlertConditionEnum.GREATER_THAN_OR_EQUAL
    assert alert.user_email == "test@example.com"
    assert alert.amount == 50000.0
    assert alert.triggered is False
    assert alert.id is None


def test_alert_schema_fields():
    alert = Alert(
        coin="eth",
        condition=AlertConditionEnum.LESS_THAN_OR_EQUAL,
        amount=3000.0,
        user_email="user@mail.com",
    )
    assert isinstance(alert.created_at, datetime)
    assert alert.triggered is False
