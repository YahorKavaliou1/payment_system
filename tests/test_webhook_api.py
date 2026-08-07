from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.deps import get_payment_service
from app.schemas.payment import PaymentWebhookResponse
from main import app


def test_payment_webhook_endpoint_returns_service_result() -> None:
    service = MagicMock()
    service.handle_webhook.return_value = PaymentWebhookResponse(
        processed=True,
        duplicate=False,
        payment_id="abc-123",
        subscription_status="active",
        expires_at=datetime(2026, 9, 6, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_payment_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.post(
            "/webhook/payment",
            json={
                "payment_id": "abc-123",
                "user_id": 42,
                "amount": 4900,
                "status": "CONFIRMED",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["processed"] is True
    assert body["duplicate"] is False
    assert body["payment_id"] == "abc-123"
    service.handle_webhook.assert_called_once()
