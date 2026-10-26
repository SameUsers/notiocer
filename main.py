import logging

from notiocer.application.use_cases.send_invoice_notifications import (
    SendInvoiceNotifications,
)
from notiocer.domain.services.invoice_notification_builder import (
    InvoiceNotificationBuilder,
)
from notiocer.domain.services.invoice_recipient_router import (
    InvoiceRecipientRouter,
)
from notiocer.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from notiocer.infrastructure.ax.employee_email_lookup import AxEmployeeEmailLookup
from notiocer.infrastructure.config.routing_rules import load_routing_rules
from notiocer.infrastructure.config.settings import get_settings
from notiocer.infrastructure.excel.openpyxl_invoice_attachment_builder import (
    OpenpyxlInvoiceAttachmentBuilder,
)
from notiocer.infrastructure.excel.openpyxl_invoice_reader import OpenpyxlInvoiceReader
from notiocer.infrastructure.excel.xlrd_invoice_reader import XlrdInvoiceReader
from notiocer.infrastructure.exchange.exchange_email_sender import ExchangeEmailSender
from notiocer.presentation.cli.invoice_report_controller import (
    InvoiceReportController,
)


def main() -> None:
    """Собирает зависимости и запускает рассылку по Excel-отчёту.

    Проверяет YAML-правила до подключения к внешним системам.
    Передаёт правила доменному сервису и закрывает соединение с AX
    после выполнения сценария, в том числе при ошибке.
    """
    settings = get_settings()
    routing_rules = load_routing_rules(settings.mailing_rules_file)
    report_path = settings.invoice_report_file.path
    if not report_path.is_file():
        raise FileNotFoundError(f'Не найден Excel-отчёт: {report_path}')

    employee_email_lookup = AxEmployeeEmailLookup(
        odbc_driver=settings.ax.odbc_driver,
        server=settings.ax.server,
        database=settings.ax.database,
        username=settings.ax.username,
        password=settings.ax.password.get_secret_value(),
        cache_path=settings.ax.cache_path,
    )

    email_sender = ExchangeEmailSender(
        username=settings.exchange.username,
        password=settings.exchange.password.get_secret_value(),
        default_body=settings.message.body,
        default_subject=settings.message.subject,
    )
    invoice_reader = (
        XlrdInvoiceReader()
        if report_path.suffix.lower() == '.xls'
        else OpenpyxlInvoiceReader()
    )

    invoice_selector = MailingInvoiceSelector(
        allowed_categories=settings.invoice_selection.allowed_categories,
        minimum_invoice_age=settings.invoice_selection.minimum_invoice_age,
    )

    recipient_router = InvoiceRecipientRouter(routing_rules=routing_rules)

    notification_builder = InvoiceNotificationBuilder(
        employee_email_lookup=employee_email_lookup
    )

    attachment_builder = OpenpyxlInvoiceAttachmentBuilder()
    send_notifications = SendInvoiceNotifications(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        recipient_router=recipient_router,
        notification_builder=notification_builder,
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )

    report_controller = InvoiceReportController(
        report_path=report_path,
        use_case=send_notifications,
    )
    employee_email_lookup.connect()
    try:
        report_controller.run()
    finally:
        employee_email_lookup.disconnect()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
    )
    main()
