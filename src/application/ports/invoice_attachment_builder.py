from collections.abc import Sequence
from typing import Protocol

from ...domain.entity.invoice import Invoice
from ..dto.email_attachment import EmailAttachment


class InvoiceAttachmentBuilder(Protocol):
    def build_attachment(self, invoices: Sequence[Invoice]) -> EmailAttachment:
        ...
