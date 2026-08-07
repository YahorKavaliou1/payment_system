from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.payment import PaymentRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.user import UserRepository
from app.schemas.payment import PaymentStatus, PaymentWebhookRequest, PaymentWebhookResponse

SUBSCRIPTION_DAYS = 30


class PaymentService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._payments = PaymentRepository(session)
        self._subscriptions = SubscriptionRepository(session)

    def handle_webhook(self, payload: PaymentWebhookRequest) -> PaymentWebhookResponse:
        if payload.status != PaymentStatus.CONFIRMED:
            return PaymentWebhookResponse(
                processed=False, duplicate=False, payment_id=payload.payment_id
            )

        if self._users.get_by_id(payload.user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User {payload.user_id} not found"
            )

        # Single transaction: payment insert + subscription activation.
        # Crash before commit rolls both back — no days left without access.
        payment_row_id = self._payments.try_insert(
            payment_id=payload.payment_id,
            user_id=payload.user_id,
            amount=payload.amount,
            status=payload.status,
        )

        if payment_row_id is None:
            # Duplicate webhook — do not extend subscription again.
            return PaymentWebhookResponse(
                processed=False, duplicate=True, payment_id=payload.payment_id
            )

        expires_at = datetime.now(timezone.utc) + timedelta(days=SUBSCRIPTION_DAYS)
        subscription = self._subscriptions.activate(
            user_id=payload.user_id, expires_at=expires_at
        )
        self._session.commit()

        return PaymentWebhookResponse(
            processed=True,
            duplicate=False,
            payment_id=payload.payment_id,
            subscription_status=subscription.status,
            expires_at=subscription.expires_at,
        )
