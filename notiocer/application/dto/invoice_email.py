from dataclasses import dataclass

from notiocer.application.dto.email_attachment import EmailAttachment
from notiocer.domain.models.invoice import Invoice


@dataclass(frozen=True)
class InvoiceEmail:
    """Получатель, счета и вложение подготовленного письма."""

    recipient_email: str
    invoices: list[Invoice]
    attachment: EmailAttachment
