from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Invoice:
    client_id: Any
    legal_entity: str | None
    subject: str | None
    invoice_number: str | None
    invoice_date: datetime | None
    invoice_amount: float | None
    balance: float | None
    currency: str | None
    category: str | None
    payment_due_date: datetime | None
    sign: str | None
    employee: str | None
    equipment_service: str | None
    transport_reference: str | None
    unloading_date: datetime | None
    sfb_curator: str | None
    shipping_date: datetime | None
    estimated_arrival_date: datetime | None
    market: str | None
    payment_service: str | None
    payment_terms_type: str | None
    contract_details: str | None
    service_type: str | None
    partial_prepayment: Any
    partial_prepayment_terms: str | None
    payment_terms: str | None
    calculated_payment_term: Any
