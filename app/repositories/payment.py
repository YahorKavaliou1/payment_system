from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Payment


class PaymentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def try_insert(
        self,
        *,
        payment_id: str,
        user_id: int,
        amount: int,
        status: str,
    ) -> int | None:
        """
        Insert a payment once.

        Returns the new primary key if inserted, None on duplicate payment_id.
        """
        stmt = (
            insert(Payment)
            .values(
                payment_id=payment_id,
                user_id=user_id,
                amount=amount,
                status=status,
            )
            .on_conflict_do_nothing(constraint="uq_payments_payment_id")
            .returning(Payment.id)
        )
        return self._session.execute(stmt).scalar_one_or_none()
