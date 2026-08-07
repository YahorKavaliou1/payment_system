from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.payment import PaymentWebhookRequest
from app.services.payment import PaymentService


def _payload(**overrides: object) -> PaymentWebhookRequest:
    data: dict[str, object] = {
        "payment_id": "abc-123",
        "user_id": 42,
        "amount": 4900,
        "status": "CONFIRMED",
    }
    data.update(overrides)
    return PaymentWebhookRequest.model_validate(data)


def _service() -> tuple[PaymentService, MagicMock, MagicMock, MagicMock, MagicMock]:
    session = MagicMock()
    service = PaymentService(session)
    users = MagicMock()
    payments = MagicMock()
    subscriptions = MagicMock()
    service._users = users
    service._payments = payments
    service._subscriptions = subscriptions
    return service, session, users, payments, subscriptions


def test_ignores_non_confirmed_status() -> None:
    service, session, users, payments, subscriptions = _service()

    result = service.handle_webhook(_payload(status="PENDING"))

    assert result.processed is False
    assert result.duplicate is False
    users.get_by_id.assert_not_called()
    payments.try_insert.assert_not_called()
    subscriptions.activate.assert_not_called()
    session.commit.assert_not_called()


def test_raises_404_when_user_missing() -> None:
    service, session, users, payments, subscriptions = _service()
    users.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.handle_webhook(_payload())

    assert exc_info.value.status_code == 404
    payments.try_insert.assert_not_called()
    subscriptions.activate.assert_not_called()
    session.commit.assert_not_called()


def test_confirmed_payment_activates_subscription() -> None:
    service, session, users, payments, subscriptions = _service()
    users.get_by_id.return_value = MagicMock(id=42)
    payments.try_insert.return_value = 1
    expires_at = datetime(2026, 9, 6, tzinfo=timezone.utc)
    subscriptions.activate.return_value = MagicMock(
        status="active", expires_at=expires_at
    )

    result = service.handle_webhook(_payload())

    assert result.processed is True
    assert result.duplicate is False
    assert result.subscription_status == "active"
    assert result.expires_at == expires_at
    payments.try_insert.assert_called_once()
    subscriptions.activate.assert_called_once()
    session.commit.assert_called_once()


def test_duplicate_payment_does_not_extend_subscription() -> None:
    service, session, users, payments, subscriptions = _service()
    users.get_by_id.return_value = MagicMock(id=42)
    payments.try_insert.return_value = None

    result = service.handle_webhook(_payload())

    assert result.processed is False
    assert result.duplicate is True
    subscriptions.activate.assert_not_called()
    session.commit.assert_not_called()
