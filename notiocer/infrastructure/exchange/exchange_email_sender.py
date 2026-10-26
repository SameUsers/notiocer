from exchangelib import (
    DELEGATE,
    Account,
    Credentials,
    FileAttachment,
    Mailbox,
    Message,
)

from notiocer.application.dto.invoice_email import InvoiceEmail


class ExchangeEmailSender:
    """Отправляет письма с XLSX-вложениями через учётную запись Exchange."""

    def __init__(
        self, username: str, password: str, default_body: str, default_subject: str
    ) -> None:
        """Подключает учётную запись Exchange и задаёт тему и текст писем."""
        self._default_body = default_body
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

    def send(self, email: InvoiceEmail) -> None:
        """Отправляет письмо и сохраняет копию без автоматического повтора при ошибке."""
        exchange_message = Message(
            account=self._account,
            subject=self._default_subject,
            body=self._default_body,
            folder=self._account.drafts,
            to_recipients=[Mailbox(email_address=email.recipient_email)],
        )

        exchange_message.attach(
            FileAttachment(
                name=email.attachment.filename,
                content=email.attachment.content,
                content_type=email.attachment.content_type,
            )
        )
        exchange_message.save()
        exchange_message.refresh()
        content = exchange_message.mime_content
        if content:
            with open(f'results/{email.recipient_email}.eml', mode='wb') as file:
                file.write(content)  # type: ignore
        # exchange_message.send_and_save()
