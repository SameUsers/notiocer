from exchangelib import (
    Account,
    DELEGATE,
    Credentials,
    Message,
    Mailbox,
    FileAttachment,
)

from src.application.dto.prepared_invoice_message import PreparedInvoiceMessage


class ExchangeEmailSender:
    def __init__(
        self,
        username: str,
        password: str,
        defult_text: str,
        default_subject: str
    ) -> None:
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

    def send_email(self, message: PreparedInvoiceMessage) -> None:
        exchange_message = Message(
            account=self._account,
            subject="Test Subject",
            body="Test Body",
            to_recipients=[
                Mailbox(email_address=message.recipient_email)
            ],
        )
        exchange_message.attach(
            FileAttachment(
                name=message.attachment.filename,
                content=message.attachment.content,
                content_type=message.attachment.content_type,
            )
        )
        exchange_message.send_and_save()
