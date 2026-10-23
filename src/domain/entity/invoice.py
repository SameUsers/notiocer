from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Invoice:
    category: str | None
    payment_terms: str | None
    invoice_date: datetime | None
    legal_entity: str | None
    subject: str | None
    invoice_number: str | None
    sign: str | None
