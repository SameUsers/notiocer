import logging

from notiocer.application.commands.send_invoice_notifications import (
    SendInvoiceNotificationsCommand,
)
from notiocer.application.dto.invoice_email import InvoiceEmail
from notiocer.application.ports.email_sender import EmailSender
from notiocer.application.ports.invoice_attachment_builder import (
    InvoiceAttachmentBuilder,
)
from notiocer.application.ports.invoice_reader import InvoiceReader
from notiocer.domain.services.invoice_notification_builder import (
    InvoiceNotificationBuilder,
)
from notiocer.domain.services.invoice_recipient_router import InvoiceRecipientRouter
from notiocer.domain.services.mailing_invoice_selector import MailingInvoiceSelector

logger = logging.getLogger(__name__)


class SendInvoiceNotifications:
    """Читает Excel-отчёт, отбирает счета и отправляет их получателям."""

    def __init__(
        self,
        attachment_builder: InvoiceAttachmentBuilder,
        invoice_reader: InvoiceReader,
        invoice_selector: MailingInvoiceSelector,
        recipient_router: InvoiceRecipientRouter,
        notification_builder: InvoiceNotificationBuilder,
        email_sender: EmailSender,
    ) -> None:
        """Принимает зависимости чтения, обработки и отправки счетов."""
        self._attachment_builder = attachment_builder
        self._invoice_reader = invoice_reader
        self._invoice_selector = invoice_selector
        self._recipient_router = recipient_router
        self._notification_builder = notification_builder
        self._email_sender = email_sender

    def execute(self, command: SendInvoiceNotificationsCommand) -> None:
        """Готовит все вложения, отправляет письма и освобождает загруженную книгу."""
        self._invoice_reader.load(report_content=command.report_content)
        try:
            invoices = self._invoice_reader.read_invoices(worksheet_index=0)
            selected_invoices = self._invoice_selector.select_invoices(invoices)
            invoices_by_recipient = self._recipient_router.route(selected_invoices)
            notifications = self._notification_builder.build(invoices_by_recipient)

            emails = [
                InvoiceEmail(
                    recipient_email=notification.recipient_email,
                    invoices=notification.invoices,
                    attachment=self._attachment_builder.build(notification.invoices),
                )
                for notification in notifications
            ]
            logger.info(
                'Счетов прочитано: %d; отобрано: %d; писем подготовлено: %d',
                len(invoices),
                len(selected_invoices),
                len(emails),
            )
            for sent_count, email in enumerate(emails, start=1):
                self._email_sender.send(email)
                logger.info('Отправка подтверждена: %d/%d', sent_count, len(emails))
        finally:
            self._invoice_reader.unload()
