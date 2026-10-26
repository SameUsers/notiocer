from notiocer.domain.models.invoice import Invoice
from notiocer.domain.models.invoice_notification import InvoiceNotification
from notiocer.domain.ports.employee_email_lookup import EmployeeEmailLookup


class InvoiceNotificationBuilder:
    """Формирует уведомления по получателям, разрешая адреса сотрудников через порт."""

    def __init__(self, employee_email_lookup: EmployeeEmailLookup) -> None:
        """Принимает поиск email по идентификатору сотрудника."""
        self._employee_email_lookup = employee_email_lookup

    def build(
        self, invoices_by_recipient: dict[str | None, list[Invoice]]
    ) -> list[InvoiceNotification]:
        """Объединяет счета по email, пропуская повторы и ненайденные адреса."""
        notifications_by_email: dict[str, InvoiceNotification] = {}
        for recipient_reference, invoices in invoices_by_recipient.items():
            if not recipient_reference:
                continue
            recipient_email = (
                recipient_reference
                if '@' in recipient_reference
                else self._employee_email_lookup.get_email(recipient_reference)
            )
            if not recipient_email or '@' not in recipient_email:
                continue
            recipient_email = recipient_email.strip()
            normalized_email = recipient_email.casefold()
            if normalized_email not in notifications_by_email:
                notifications_by_email[normalized_email] = InvoiceNotification(
                    recipient_email=recipient_email,
                    invoices=[],
                )
            notification_invoices = notifications_by_email[normalized_email].invoices
            for invoice in invoices:
                if invoice not in notification_invoices:
                    notification_invoices.append(invoice)
        return list(notifications_by_email.values())
