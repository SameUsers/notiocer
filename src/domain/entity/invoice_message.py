from dataclasses import dataclass

from .invoice import Invoice


@dataclass(frozen=True)
class InvoiceMessage:
    recipient_email: str
    invoices: list[Invoice]
