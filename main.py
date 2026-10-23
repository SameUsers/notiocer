from pathlib import Path

from src.infra.openpyxl_invoice_reader import OpenpyxlInvoiceReader
from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.interactors.create_mailing_list import CreateMailingListInteractor
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector


def main() -> None:
    invoice_reader = OpenpyxlInvoiceReader()
    invoice_selector = MailingInvoiceSelector()
    interactor = CreateMailingListInteractor(invoice_reader=invoice_reader, invoice_selector=invoice_selector)
    workbook_path = Path("tests/test_files/Драфт авторассылки по просрочке предоплат до загрузки.xlsx")
    command = CreateMailingListCommand(excel_bytes=workbook_path.read_bytes())
    selected_invoices = interactor.execute(command=command)
    for invoice in selected_invoices:
        print(invoice)

if __name__ == "__main__":
    main()
