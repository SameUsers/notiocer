from dataclasses import dataclass

from notiocer.domain.models.invoice import Invoice


@dataclass(frozen=True)
class InvoiceNotification:
    """Почтовый адрес получателя и относящиеся к нему счета."""

    recipient_email: str
    invoices: list[Invoice]
