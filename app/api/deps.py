from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.payment import PaymentService


def get_payment_service(db: Annotated[Session, Depends(get_db)]) -> PaymentService:
    return PaymentService(db)
