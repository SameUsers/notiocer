import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from src.infra.excel_readers.openpyxl_invoice_reader import OpenpyxlInvoiceReader
from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.interactors.create_mailing_list import CreateMailingListInteractor
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from src.domain.services.recipient_mailing_list_builder import RecipientMailingListBuilder
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder
from src.infra.settings import get_settings


def main() -> None:
    settings = get_settings()
    invoice_reader = OpenpyxlInvoiceReader()
    invoice_selector = MailingInvoiceSelector(
        allowed_categories=settings.invoice_selection.allowed_categories,
        minimum_invoice_age=settings.invoice_selection.minimum_invoice_age,
    )
    mailing_list_builder = RecipientMailingListBuilder()
    message_builder = InvoiceMessageBuilder()
    interactor = CreateMailingListInteractor(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        mailing_list_builder=mailing_list_builder,
        message_builder=message_builder,
    )
    workbook_path = Path("tests/test_files/Драфт авторассылки по просрочке предоплат до загрузки.xlsx")
    command = CreateMailingListCommand(excel_bytes=workbook_path.read_bytes())
    messages = interactor.execute(command=command)
    with Path("test.json").open("w", encoding="utf-8") as output_file:
        json.dump(
            [asdict(message) for message in messages], output_file,
            ensure_ascii=False, indent=4, default=datetime.isoformat,
        )

if __name__ == "__main__":
    main()
