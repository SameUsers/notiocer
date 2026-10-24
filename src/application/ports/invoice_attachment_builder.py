from collections.abc import Sequence
from typing import Protocol

from ...domain.entity.invoice import Invoice
from ..dto.email_attachment import EmailAttachment


class InvoiceAttachmentBuilder(Protocol):
    """Протокол для формирования email-вложения из набора счетов."""

    def build_attachment(self, invoices: Sequence[Invoice]) -> EmailAttachment:
        """Формирует email-вложение, содержащее указанные счета.

        Args:
            invoices: Счета, которые нужно включить во вложение.

        Returns:
            Email-вложение, сформированное из переданных счетов.
        """
        ...
