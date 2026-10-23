from pathlib import Path

from src.infra.excel_readers.xlrd_invoice_reader import XlrdInvoiceReader
from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.interactors.create_mailing_list import CreateMailingListInteractor
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from src.domain.services.recipient_mailing_list_builder import RecipientMailingListBuilder
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder
from src.infra.settings import get_settings
from src.infra.excel_writers.openpyxl_invoice_attachment_builder import OpenpyxlInvoiceAttachmentBuilder
from src.infra.exchange.exchange_email_sender import ExchangeEmailSender


def main() -> None:
    settings = get_settings()
    if settings.exchange is None:
        raise ValueError("Укажите exchange__username и exchange__password в окружении или .env")
    email_sender = ExchangeEmailSender(
        username=settings.exchange.username,
        password=settings.exchange.password.get_secret_value(),
        defult_text=settings.message.mail_tex,
        default_subject=settings.message.mail_subject
    )
    invoice_reader = XlrdInvoiceReader()
    invoice_selector = MailingInvoiceSelector(
        allowed_categories=settings.invoice_selection.allowed_categories,
        minimum_invoice_age=settings.invoice_selection.minimum_invoice_age,
    )
    mailing_list_builder = RecipientMailingListBuilder()
    message_builder = InvoiceMessageBuilder()
    attachment_builder = OpenpyxlInvoiceAttachmentBuilder()
    interactor = CreateMailingListInteractor(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        mailing_list_builder=mailing_list_builder,
        message_builder=message_builder,
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )
    workbook_path = Path("tests/test_files/DZ_Report.xls")
    command = CreateMailingListCommand(excel_bytes=workbook_path.read_bytes())
    interactor.execute(command=command)

if __name__ == "__main__":
    main()
