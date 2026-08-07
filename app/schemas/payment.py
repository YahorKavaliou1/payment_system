from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatus(StrEnum):
    CONFIRMED = "CONFIRMED"


class PaymentWebhookRequest(BaseModel):
    payment_id: str = Field(..., min_length=1, max_length=255)
    user_id: int = Field(..., gt=0)
    amount: int = Field(..., gt=0)
    status: str


class PaymentWebhookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    processed: bool
    duplicate: bool
    payment_id: str
    subscription_status: str | None = None
    expires_at: datetime | None = None
