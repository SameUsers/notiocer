from ...application.ports.employee_email_lookup import EmployeeEmailLookup
from ..entity.invoice import Invoice
from ..entity.invoice_message import InvoiceMessage


class InvoiceMessageBuilder:
    """Формирует сообщения со счетами для каждого получателя из сгруппированных счетов."""

    def __init__(self, employee_email_lookup: EmployeeEmailLookup) -> None:
        """Инициализирует построитель.

        Args:
            employee_email_lookup: Определяет адреса электронной почты по идентификаторам сотрудников.
        """
        self._employee_email_lookup = employee_email_lookup

    def build_messages(
        self, invoices_by_recipient: dict[str | None, list[Invoice]]
    ) -> list[InvoiceMessage]:
        """Формирует сообщения со счетами для каждого корректного получателя.

        Получатели, которые уже являются адресами электронной почты, используются как есть;
        остальные непустые получатели рассматриваются как идентификаторы сотрудников
        и преобразуются в email через поиск. Получатели с пустыми или
        неразрешёнными email пропускаются.

        Args:
            invoices_by_recipient: Отображение получателя (email или идентификатор
                сотрудника) на счета, адресованные ему.

        Returns:
            Список сообщений со счетами, по одному на каждого корректного получателя.
        """
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
