from pathlib import Path

from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.interactors.create_mailing_list_from_excel import (
    CreateMailingListFromExcelInteractor,
)
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from src.domain.services.recipient_mailing_list_builder import (
    RecipientMailingListBuilder,
)
from src.infra.ax_adapter.employee_email_lookup import AxEmployeeEmailLookup
from src.infra.excel_readers.xlrd_invoice_reader import XlrdInvoiceReader
from src.infra.excel_writers.openpyxl_invoice_attachment_builder import (
    OpenpyxlInvoiceAttachmentBuilder,
)
from src.infra.exchange.exchange_email_sender import ExchangeEmailSender
from src.infra.settings import get_settings


def main() -> None:
    settings = get_settings()
    employee_email_lookup = AxEmployeeEmailLookup(
        odbc_driver=settings.ax.odbc_driver,
        server=settings.ax.server,
        database=settings.ax.database,
        username=settings.ax.username,
        password=settings.ax.password.get_secret_value(),
    )

    email_sender = ExchangeEmailSender(
        username=settings.exchange.username,
        password=settings.exchange.password.get_secret_value(),
        defult_text=settings.message.mail_tex,
        default_subject=settings.message.mail_subject,
    )
    invoice_reader = XlrdInvoiceReader()
    invoice_selector = MailingInvoiceSelector(
        allowed_categories=settings.invoice_selection.allowed_categories,
        minimum_invoice_age=settings.invoice_selection.minimum_invoice_age,
    )
    mailing_list_builder = RecipientMailingListBuilder()
    message_builder = InvoiceMessageBuilder(employee_email_lookup=employee_email_lookup)
    attachment_builder = OpenpyxlInvoiceAttachmentBuilder()
    interactor = CreateMailingListFromExcelInteractor(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        mailing_list_builder=mailing_list_builder,
        message_builder=message_builder,
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )
    workbook_path = Path('tests/test_files/DZ_Report.xls')
    command = CreateMailingListCommand(excel_bytes=workbook_path.read_bytes())
    employee_email_lookup.connect()
    try:
        interactor.execute(command=command)
    finally:
        employee_email_lookup.disconnect()


if __name__ == '__main__':
    main()
