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
from notiocer.application.ports.report_generator import ReportGenerator
from notiocer.domain.services.invoice_notification_builder import (
    InvoiceNotificationBuilder,
)
from notiocer.domain.services.invoice_recipient_router import InvoiceRecipientRouter
from notiocer.domain.services.mailing_invoice_selector import MailingInvoiceSelector

logger = logging.getLogger(__name__)


class SendInvoiceNotifications:
    """Запускает генерацию отчёта, отбор счетов и рассылку уведомлений."""

    def __init__(
        self,
        attachment_builder: InvoiceAttachmentBuilder,
        invoice_reader: InvoiceReader,
        invoice_selector: MailingInvoiceSelector,
        recipient_router: InvoiceRecipientRouter,
        notification_builder: InvoiceNotificationBuilder,
        email_sender: EmailSender,
        report_generator: ReportGenerator,
    ) -> None:
        """Принимает зависимости генерации отчёта, чтения и рассылки счетов."""
        self._attachment_builder = attachment_builder
        self._invoice_reader = invoice_reader
        self._invoice_selector = invoice_selector
        self._recipient_router = recipient_router
        self._notification_builder = notification_builder
        self._email_sender = email_sender
        self._report_generator = report_generator

    def execute(self, command: SendInvoiceNotificationsCommand) -> None:
        """Генерирует отчёт, готовит вложения, отправляет письма и освобождает книгу."""
        self._report_generator.generate()
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
