from collections.abc import Sequence
from typing import Protocol

from notiocer.application.dto.email_attachment import EmailAttachment
from notiocer.domain.models.invoice import Invoice


class InvoiceAttachmentBuilder(Protocol):
    """Порт создания почтового вложения со счетами."""

    def build(self, invoices: Sequence[Invoice]) -> EmailAttachment:
        """Создаёт вложение с переданными счетами."""
        ...
