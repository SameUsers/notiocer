from ...domain.entity.invoice import Invoice
from ..commands.create_mailing_list import CreateMailingListCommand
from ..ports.invoice_excel_reader import InvoiceExcelReader
from ...domain.services.mailing_invoice_selector import MailingInvoiceSelector


class CreateMailingListInteractor:
    def __init__(self, invoice_reader: InvoiceExcelReader, invoice_selector: MailingInvoiceSelector) -> None:
        self._invoice_reader = invoice_reader
        self._invoice_selector = invoice_selector

    def execute(self, command: CreateMailingListCommand) -> set[Invoice]:
        self._invoice_reader.load(excel_bytes=command.excel_bytes)
        try:
            all_invoices = self._invoice_reader.read_invoices(worksheet_index=0)
            selected_invoices = self._invoice_selector.select_invoices(all_invoices)
            return selected_invoices
        finally:
            self._invoice_reader.unload()
