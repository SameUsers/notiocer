from exchangelib import (
    Account,
    DELEGATE,
    Credentials,
    Message,
    Mailbox,
    FileAttachment,
)

from src.application.dto.prepared_invoice_message import PreparedInvoiceMessage
from pathlib import Path
from uuid import uuid4

class ExchangeEmailSender:
    def __init__(
        self,
        username: str,
        password: str,
        defult_text: str,
        default_subject: str
    ) -> None:
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
        self.counter = 0

    def send_email(self, message: PreparedInvoiceMessage) -> None:
        exchange_message = Message(
            account=self._account,
            subject=self._default_subject,
            body=self._default_body,
            folder=self._account.drafts,
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