from typing import Protocol

from ..dto.prepared_invoice_message import PreparedInvoiceMessage


class EmailSender(Protocol):
    def send_email(self, message: PreparedInvoiceMessage) -> None: ...
