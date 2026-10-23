from datetime import datetime, timedelta
from io import BytesIO

import pytest
from openpyxl import Workbook, load_workbook

from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.ports.email_sender import EmailSender
from src.application.interactors.create_mailing_list import CreateMailingListInteractor
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from src.domain.services.recipient_mailing_list_builder import RecipientMailingListBuilder
from src.infra.excel_readers.openpyxl_invoice_reader import OpenpyxlInvoiceReader
from src.infra.excel_writers.openpyxl_invoice_attachment_builder import OpenpyxlInvoiceAttachmentBuilder


@pytest.fixture
def invoice_report():
    workbook = Workbook()
    try:
        worksheet = workbook.active
        worksheet.append([
            "Категория", "Дата счета", "Предоплата до загрузки", "Сервис для срока оплаты",
            "Рынок", "Сотрудник", "Полный номер счета",
        ])
        worksheet.append(["Д0", datetime(2000, 1, 1), "да", "Авиа", "РБ", "Сотрудник", "INV-001"])
        worksheet.append(["Д0", datetime(2000, 1, 1), "да", "Авиа", "РФ", "Сотрудник", "INV-002"])
        with BytesIO() as buffer:
            workbook.save(buffer)
            return buffer.getvalue()
    finally:
        workbook.close()


def create_interactor(reader, attachment_builder, email_sender):
    return CreateMailingListInteractor(
        invoice_reader=reader,
        invoice_selector=MailingInvoiceSelector({"Д0"}, timedelta(days=3)),
        mailing_list_builder=RecipientMailingListBuilder(),
        message_builder=InvoiceMessageBuilder(),
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )


def test_create_mailing_list_sends_each_recipients_attachment(invoice_report, email_sender):
    reader = OpenpyxlInvoiceReader()
    interactor = create_interactor(reader, OpenpyxlInvoiceAttachmentBuilder(), email_sender)

    result = interactor.execute(CreateMailingListCommand(invoice_report))

    assert result is None
    assert email_sender.send_email.call_count == 2
    messages = [call.args[0] for call in email_sender.send_email.call_args_list]

    assert {message.recipient_email for message in messages} == {
        "CM_Air_BY@stalogistic.com", "cm-air-ru@stalogistic.com",
    }
    expected_numbers = {"CM_Air_BY@stalogistic.com": "INV-001", "cm-air-ru@stalogistic.com": "INV-002"}
    for message in messages:
        workbook = load_workbook(BytesIO(message.attachment.content), data_only=True)
        try:
            rows = list(workbook.active.iter_rows(values_only=True))
            assert len(rows) == 2
            assert dict(zip(rows[0], rows[1]))["Полный номер счета"] == expected_numbers[message.recipient_email]
        finally:
            workbook.close()
    with pytest.raises(ValueError):
        _ = reader.workbook



def test_attachment_failure_propagates_and_unloads_reader(invoice_report, mocker, email_sender):
    reader = OpenpyxlInvoiceReader()
    attachment_builder = OpenpyxlInvoiceAttachmentBuilder()
    attachment_error = OSError("Cannot create attachment")
    mocker.patch.object(attachment_builder, "build_attachment", side_effect=attachment_error)
    interactor = create_interactor(reader, attachment_builder, email_sender)

    with pytest.raises(OSError) as error:
        interactor.execute(CreateMailingListCommand(invoice_report))

    email_sender.send_email.assert_not_called()
    assert error.value is attachment_error
    with pytest.raises(ValueError):
        _ = reader.workbook


@pytest.fixture
def email_sender(mocker):
    return mocker.create_autospec(EmailSender, instance=True, spec_set=True)


def test_sender_failure_propagates_and_unloads_reader(invoice_report, email_sender):
    reader = OpenpyxlInvoiceReader()
    send_error = RuntimeError("Exchange is unavailable")
    email_sender.send_email.side_effect = send_error
    interactor = create_interactor(reader, OpenpyxlInvoiceAttachmentBuilder(), email_sender)

    with pytest.raises(RuntimeError) as error:
        interactor.execute(CreateMailingListCommand(invoice_report))

    assert error.value is send_error
    email_sender.send_email.assert_called_once()
    with pytest.raises(ValueError):
        _ = reader.workbook


def test_empty_report_does_not_send_emails(invoice_report, email_sender):
    workbook = load_workbook(BytesIO(invoice_report))
    try:
        workbook.active.delete_rows(2, 2)
        with BytesIO() as buffer:
            workbook.save(buffer)
            empty_report = buffer.getvalue()
    finally:
        workbook.close()
    reader = OpenpyxlInvoiceReader()
    interactor = create_interactor(reader, OpenpyxlInvoiceAttachmentBuilder(), email_sender)

    assert interactor.execute(CreateMailingListCommand(empty_report)) is None
    email_sender.send_email.assert_not_called()
    with pytest.raises(ValueError):
        _ = reader.workbook
