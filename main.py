from pathlib import Path

from src.infra.excel_readers.xlrd_invoice_reader import XlrdInvoiceReader
from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.interactors.create_mailing_list import CreateMailingListInteractor
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from src.domain.services.recipient_mailing_list_builder import RecipientMailingListBuilder
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder
from src.infra.settings import get_settings
from src.infra.excel_writers.openpyxl_invoice_attachment_builder import OpenpyxlInvoiceAttachmentBuilder


def main() -> None:
    settings = get_settings()
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
    )
    workbook_path = Path("tests/test_files/DZ_Report.xls")
    command = CreateMailingListCommand(excel_bytes=workbook_path.read_bytes())
    messages = interactor.execute(command=command)

    for index, message in enumerate(messages[:5]):
        Path(f"{index}.xlsx").write_bytes(message.attachment.content)

if __name__ == "__main__":
    main()
