from ...domain.services.invoice_message_builder import InvoiceMessageBuilder
from ...domain.services.mailing_invoice_selector import MailingInvoiceSelector
from ...domain.services.recipient_mailing_list_builder import (
    RecipientMailingListBuilder,
)
from ..commands.create_mailing_list import CreateMailingListCommand
from ..dto.prepared_invoice_message import PreparedInvoiceMessage
from ..ports.email_sender import EmailSender
from ..ports.invoice_attachment_builder import InvoiceAttachmentBuilder
from ..ports.invoice_excel_reader import InvoiceExcelReader


class CreateMailingListFromExcelInteractor:
    """Сценарий использования, который формирует и отправляет списки рассылки счетов из данных Excel.

    Оркестрирует полный поток: чтение счетов из книги Excel,
    отбор нужных, группировку по получателям, формирование
    сообщений для каждого получателя с вложениями и их отправку по email.
    """

    def __init__(
        self,
        attachment_builder: InvoiceAttachmentBuilder,
        invoice_reader: InvoiceExcelReader,
        invoice_selector: MailingInvoiceSelector,
        mailing_list_builder: RecipientMailingListBuilder,
        message_builder: InvoiceMessageBuilder,
        email_sender: EmailSender,
    ) -> None:
        """Инициализирует интерактор его взаимодействующими сервисами.

        Args:
            attachment_builder: Формирует email-вложения из счетов.
            invoice_reader: Загружает и читает счета из книги Excel.
            invoice_selector: Отбирает счета, которые должны быть разосланы.
            mailing_list_builder: Группирует счета по получателю.
            message_builder: Формирует сообщения со счетами для каждого получателя.
            email_sender: Отправляет подготовленные сообщения по email.
        """
        self._attachment_builder = attachment_builder
        self._invoice_reader = invoice_reader
        self._invoice_selector = invoice_selector
        self._mailing_list_builder = mailing_list_builder
        self._message_builder = message_builder
        self._email_sender = email_sender

    def execute(self, command: CreateMailingListCommand) -> None:
        """Выполняет поток создания и отправки списка рассылки.

        Загружает книгу из сырых байтов команды, читает счета
        с первого листа, отбирает и группирует их по получателю,
        формирует по одному сообщению на получателя с вложением и отправляет
        каждое сообщение. Книга всегда выгружается после завершения.

        Args:
            command: Входные данные, содержащие байты книги Excel.
        """
        self._invoice_reader.load(excel_bytes=command.excel_bytes)
        try:
            all_invoices = self._invoice_reader.read_invoices(worksheet_index=0)
            selected_invoices = self._invoice_selector.select_invoices(all_invoices)
            invoices_by_recipient = self._mailing_list_builder.build(selected_invoices)
            messages = self._message_builder.build_messages(invoices_by_recipient)

            prepared_messages = [
                PreparedInvoiceMessage(
                    recipient_email=message.recipient_email,
                    invoices=message.invoices,
                    attachment=self._attachment_builder.build_attachment(
                        message.invoices
                    ),
                )
                for message in messages
            ]
            for message in prepared_messages:
                self._email_sender.send_email(message)
        finally:
            self._invoice_reader.unload()
