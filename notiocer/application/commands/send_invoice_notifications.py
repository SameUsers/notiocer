from dataclasses import dataclass


@dataclass
class SendInvoiceNotificationsCommand:
    """Байты исходного Excel-отчёта для формирования рассылки."""

    report_content: bytes
