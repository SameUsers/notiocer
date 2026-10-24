from dataclasses import dataclass

from .invoice import Invoice


@dataclass(frozen=True)
class InvoiceMessage:
    """Неизменяемое сообщение, группирующее счета для одного получателя.

    Атрибуты:
        recipient_email: Адрес электронной почты, для которого предназначено сообщение.
        invoices: Счета, которые нужно включить в сообщение.
    """

    recipient_email: str
    invoices: list[Invoice]
