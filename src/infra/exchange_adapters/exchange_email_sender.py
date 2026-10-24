from exchangelib import (
    DELEGATE,
    Account,
    Credentials,
    FileAttachment,
    Mailbox,
    Message,
)
from src.utils.retry_decorator import retry_sync
from src.application.dto.prepared_invoice_message import PreparedInvoiceMessage


class ExchangeEmailSender:
    """Отправляет подготовленные сообщения со счетами через Microsoft Exchange.

    Подключается к учётной записи Exchange при создании с помощью
    autodiscover и отправляет каждое сообщение как email с настроенными
    темой и телом по умолчанию, а также вложением из сообщения.
    """

    def __init__(
        self, username: str, password: str, defult_text: str, default_subject: str
    ) -> None:
        """Инициализирует отправитель и подключается к учётной записи Exchange.

        Args:
            username: Адрес учётной записи Exchange, используемый для
                аутентификации и как адрес отправителя.
            password: Пароль для учётной записи Exchange.
            defult_text: Текст тела по умолчанию, используемый для каждого
                исходящего письма.
            default_subject: Тема по умолчанию, используемая для каждого
                исходящего письма.
        """
        self._default_body = defult_text
        self._default_subject = default_subject
        credentials = Credentials(
            username=username,
            password=password,
        )
        self._account = Account(
            primary_smtp_address=username,
            access_type=DELEGATE,
            autodiscover=True,
            credentials=credentials,
        )

    @retry_sync(count=3, delay=2)
    def send_email(self, message: PreparedInvoiceMessage) -> None:
        """Отправляет переданное подготовленное сообщение со счетами.

        Формирует сообщение Exchange с темой и телом по умолчанию,
        прикрепляет вложение из сообщения и отправляет его, сохраняя
        копию. При возникновении исключения вызов повторяется до трёх
        раз с задержкой в 2 секунды между попытками (см. декоратор
        :func:`retry_sync`).

        Args:
            message: Подготовленное сообщение со счетами, которое нужно доставить.

        Raises:
            Exception: Последнее исключение, возникшее после исчерпания
                всех попыток отправки.
        """
        exchange_message = Message(
            account=self._account,
            subject=self._default_subject,
            body=self._default_body,
            folder=self._account.drafts,
            to_recipients=[Mailbox(email_address=message.recipient_email)],
        )

        exchange_message.attach(
            FileAttachment(
                name=message.attachment.filename,
                content=message.attachment.content,
                content_type=message.attachment.content_type,
            )
        )
        exchange_message.send_and_save()
