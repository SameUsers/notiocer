from ..dto.prepared_invoice_message import PreparedInvoiceMessage
from ..commands.create_mailing_list import CreateMailingListCommand
from ..ports.invoice_excel_reader import InvoiceExcelReader
from ...domain.services.mailing_invoice_selector import MailingInvoiceSelector
from ...domain.services.recipient_mailing_list_builder import RecipientMailingListBuilder
from ...domain.services.invoice_message_builder import InvoiceMessageBuilder
from ..ports.employee_email_lookup import EmployeeEmailLookup
from ..ports.invoice_attachment_builder import InvoiceAttachmentBuilder

class CreateMailingListInteractor:
    def __init__(
        self,
        attachment_builder: InvoiceAttachmentBuilder,
        invoice_reader: InvoiceExcelReader,
        invoice_selector: MailingInvoiceSelector,
        mailing_list_builder: RecipientMailingListBuilder,
        message_builder: InvoiceMessageBuilder,
        employee_email_lookup: EmployeeEmailLookup | None = None,
    ) -> None:
        self._employee_email_lookup = employee_email_lookup
        self._attachment_builder = attachment_builder
        self._invoice_reader = invoice_reader
        self._invoice_selector = invoice_selector
        self._mailing_list_builder = mailing_list_builder
        self._message_builder = message_builder

    def execute(self, command: CreateMailingListCommand) -> list[PreparedInvoiceMessage]:
        self._invoice_reader.load(excel_bytes=command.excel_bytes)
        try:
            all_invoices = self._invoice_reader.read_invoices(worksheet_index=0)
            selected_invoices = self._invoice_selector.select_invoices(all_invoices)
            invoices_by_recipient = self._mailing_list_builder.build(selected_invoices)
            messages = self._message_builder.build_messages(invoices_by_recipient)

            return [
                PreparedInvoiceMessage(
                    recipient_email=message.recipient_email,
                    invoices=message.invoices,
                    attachment=self._attachment_builder.build_attachment(message.invoices),
                )
                for message in messages
            ]
        finally:
            self._invoice_reader.unload()
