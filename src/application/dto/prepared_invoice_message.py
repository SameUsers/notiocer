from dataclasses import dataclass

from ...domain.entity.invoice import Invoice
from .email_attachment import EmailAttachment


@dataclass(frozen=True)
class PreparedInvoiceMessage:
    recipient_email: str
    invoices: list[Invoice]
    attachment: EmailAttachment
