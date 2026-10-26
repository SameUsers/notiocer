from typing import Protocol

from notiocer.application.commands.send_invoice_notifications import (
    SendInvoiceNotificationsCommand,
)


class SendInvoiceNotificationsUseCase(Protocol):
    """Контракт формирования и отправки рассылки из Excel-отчёта."""

    def execute(self, command: SendInvoiceNotificationsCommand) -> None:
        """Формирует и отправляет рассылку по переданному отчёту."""
        ...
