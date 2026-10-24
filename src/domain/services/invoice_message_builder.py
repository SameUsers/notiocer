from ...application.ports.employee_email_lookup import EmployeeEmailLookup
from ..entity.invoice import Invoice
from ..entity.invoice_message import InvoiceMessage


class InvoiceMessageBuilder:
    def __init__(self, employee_email_lookup: EmployeeEmailLookup) -> None:
        self._employee_email_lookup = employee_email_lookup

    def build_messages(
        self, invoices_by_recipient: dict[str | None, list[Invoice]]
    ) -> list[InvoiceMessage]:
        messages: list[InvoiceMessage] = []
        for recipient, invoices in invoices_by_recipient.items():
            if not recipient:
                continue
            recipient_email = (
                recipient
                if '@' in recipient
                else self._employee_email_lookup.get_email(recipient)
            )
            if not recipient_email or '@' not in recipient_email:
                continue
            message = InvoiceMessage(recipient_email=recipient_email, invoices=invoices)
            messages.append(message)
        return messages
