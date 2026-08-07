from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_payment_service
from app.schemas.payment import PaymentWebhookRequest, PaymentWebhookResponse
from app.services.payment import PaymentService

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/payment", response_model=PaymentWebhookResponse)
def payment_webhook(
    payload: PaymentWebhookRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentWebhookResponse:
    return service.handle_webhook(payload)
