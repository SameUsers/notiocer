from exchangelib import (
    DELEGATE,
    Account,
    Credentials,
    FileAttachment,
    Mailbox,
    Message,
)

from src.application.dto.prepared_invoice_message import PreparedInvoiceMessage


class ExchangeEmailSender:
    """Sends prepared invoice messages via Microsoft Exchange.

    Connects to an Exchange account on construction using autodiscover
    and sends each message as an email with the configured default
    subject and body, plus the message's attachment.
    """

    def __init__(
        self, username: str, password: str, defult_text: str, default_subject: str
    ) -> None:
        """Initialize the sender and connect to the Exchange account.

        Args:
            username: Exchange account address used for authentication
                and as the sender address.
            password: Password for the Exchange account.
            defult_text: Default body text used for every outgoing email.
            default_subject: Default subject used for every outgoing email.
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

    def send_email(self, message: PreparedInvoiceMessage) -> None:
        """Send the given prepared invoice message.

        Builds an Exchange message with the default subject and body,
        attaches the message's attachment, and sends it while saving a
        copy.

        Args:
            message: The prepared invoice message to deliver.
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
