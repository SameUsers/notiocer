from typing import Protocol

from ..dto.prepared_invoice_message import PreparedInvoiceMessage


class EmailSender(Protocol):
    """Протокол для отправки подготовленных сообщений со счетами по email."""

    def send_email(self, message: PreparedInvoiceMessage) -> None:
        """Отправляет переданное подготовленное сообщение со счетами.

        Args:
            message: Сообщение со счетами, которое нужно доставить.
        """
        ...
