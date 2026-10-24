from dataclasses import dataclass

from ...domain.entity.invoice import Invoice
from .email_attachment import EmailAttachment


@dataclass(frozen=True)
class PreparedInvoiceMessage:
    """Неизменяемое email-сообщение, готовое к отправке получателю.

    Объединяет адрес получателя, счета, к которым оно относится, и
    вложение, которое должно сопровождать сообщение.

    Атрибуты:
        recipient_email: Адрес электронной почты, на который будет отправлено сообщение.
        invoices: Счета, охватываемые этим сообщением.
        attachment: Файл, прикреплённый к сообщению.
    """

    recipient_email: str
    invoices: list[Invoice]
    attachment: EmailAttachment
