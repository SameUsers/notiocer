from ..entity.invoice import Invoice
from ..entity.invoice_message import InvoiceMessage

class InvoiceMessageBuilder:

    def build_messages(self, invoices_by_recipient: dict[str, list[Invoice]]) -> list[InvoiceMessage]:
        messages = []
        for recipient_email, invoices in invoices_by_recipient.items():
            if "@" not in recipient_email:
                continue
            message = InvoiceMessage(recipient_email=recipient_email, invoices=invoices)
            messages.append(message)
        return messages
