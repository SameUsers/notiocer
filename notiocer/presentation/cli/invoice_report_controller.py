from pathlib import Path

from notiocer.application.commands.send_invoice_notifications import (
    SendInvoiceNotificationsCommand,
)
from notiocer.application.ports.send_invoice_notifications import (
    SendInvoiceNotificationsUseCase,
)


class InvoiceReportController:
    """Читает локальный Excel-отчёт и передаёт его сценарию рассылки."""

    def __init__(
        self, report_path: Path, use_case: SendInvoiceNotificationsUseCase
    ) -> None:
        """Принимает путь к отчёту и сценарий его обработки."""
        self._report_path = report_path
        self._use_case = use_case

    def run(self) -> None:
        """Читает отчёт и запускает отправку уведомлений."""
        report_content = self._report_path.read_bytes()
        command = SendInvoiceNotificationsCommand(report_content=report_content)
        self._use_case.execute(command=command)
