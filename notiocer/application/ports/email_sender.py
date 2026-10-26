from typing import Protocol

from notiocer.application.dto.invoice_email import InvoiceEmail


class EmailSender(Protocol):
    """Порт отправки подготовленных писем со счетами."""

    def send(self, email: InvoiceEmail) -> None:
        """Отправляет письмо с подготовленным вложением."""
        ...
