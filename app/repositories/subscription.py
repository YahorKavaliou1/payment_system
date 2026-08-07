from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Subscription


class SubscriptionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user_id(self, user_id: int) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def activate(self, user_id: int, expires_at: datetime) -> Subscription:
        """Set status and expires_at together so access and remaining days stay in sync."""
        subscription = self.get_by_user_id(user_id)
        if subscription is None:
            subscription = Subscription(
                user_id=user_id,
                status="active",
                expires_at=expires_at,
            )
            self._session.add(subscription)
        else:
            subscription.status = "active"
            subscription.expires_at = expires_at
        self._session.flush()
        return subscription
