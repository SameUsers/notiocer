from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.dto.email_attachment import EmailAttachment
from src.application.dto.prepared_invoice_message import PreparedInvoiceMessage
from src.application.interactors.create_mailing_list_from_excel import (
    CreateMailingListFromExcelInteractor,
)
from src.application.ports.email_sender import EmailSender
from src.application.ports.invoice_attachment_builder import InvoiceAttachmentBuilder
from src.application.ports.invoice_excel_reader import InvoiceExcelReader
from src.domain.entity.invoice_message import InvoiceMessage
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector
from src.domain.services.recipient_mailing_list_builder import (
    RecipientMailingListBuilder,
)


def test_execute_sends_invoice_messages_and_unloads_reader(
    mocker: MockerFixture, invoice_factory, attachment_builder, email_sender
):
    command = CreateMailingListCommand(excel_bytes=b'excel content')
    invoices = [
        invoice_factory(
            category='Предоплата',
            payment_terms='До загрузки',
            invoice_date=datetime(2000, 10, 1),
            sign='да',
        ),
        invoice_factory(None, None, None, None),
    ]
    invoice_reader = mocker.create_autospec(
        InvoiceExcelReader, instance=True, spec_set=True
    )
    invoice_reader.read_invoices.return_value = invoices
    selected_invoices = {invoices[0]}
    invoice_selector = mocker.create_autospec(
        MailingInvoiceSelector, instance=True, spec_set=True
    )
    invoice_selector.select_invoices.return_value = selected_invoices
    mailing_list_builder = mocker.create_autospec(
        RecipientMailingListBuilder, instance=True, spec_set=True
    )
    invoices_by_recipient = {'recipient@example.com': [invoices[0]]}
    mailing_list_builder.build.return_value = invoices_by_recipient
    messages = [
        InvoiceMessage(recipient_email='recipient@example.com', invoices=[invoices[0]])
    ]
    message_builder = mocker.create_autospec(
        InvoiceMessageBuilder, instance=True, spec_set=True
    )
    message_builder.build_messages.return_value = messages
    interactor = CreateMailingListFromExcelInteractor(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        mailing_list_builder=mailing_list_builder,
        message_builder=message_builder,
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )

    result = interactor.execute(command=command)

    assert result is None
    email_sender.send_email.assert_called_once_with(
        PreparedInvoiceMessage(
            recipient_email=messages[0].recipient_email,
            invoices=messages[0].invoices,
            attachment=attachment_builder.build_attachment.return_value,
        )
    )
    attachment_builder.build_attachment.assert_called_once_with(messages[0].invoices)
    mailing_list_builder.build.assert_called_once_with(selected_invoices)
    message_builder.build_messages.assert_called_once_with(invoices_by_recipient)
    invoice_selector.select_invoices.assert_called_once_with(invoices)
    invoice_reader.load.assert_called_once_with(excel_bytes=command.excel_bytes)
    invoice_reader.read_invoices.assert_called_once_with(worksheet_index=0)
    invoice_reader.unload.assert_called_once_with()


def test_execute_unloads_reader_and_propagates_read_error(
    mocker: MockerFixture, attachment_builder, email_sender
):
    command = CreateMailingListCommand(excel_bytes=b'excel content')
    invoice_reader = mocker.create_autospec(
        InvoiceExcelReader, instance=True, spec_set=True
    )
    read_error = ValueError('Ошибка чтения счетов')
    invoice_reader.read_invoices.side_effect = read_error
    invoice_selector = mocker.create_autospec(
        MailingInvoiceSelector, instance=True, spec_set=True
    )
    mailing_list_builder = mocker.create_autospec(
        RecipientMailingListBuilder, instance=True, spec_set=True
    )
    message_builder = mocker.create_autospec(
        InvoiceMessageBuilder, instance=True, spec_set=True
    )
    interactor = CreateMailingListFromExcelInteractor(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        mailing_list_builder=mailing_list_builder,
        message_builder=message_builder,
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )

    with pytest.raises(ValueError) as error:
        interactor.execute(command=command)

    email_sender.send_email.assert_not_called()
    attachment_builder.build_attachment.assert_not_called()
    assert error.value is read_error
    invoice_selector.select_invoices.assert_not_called()
    mailing_list_builder.build.assert_not_called()
    message_builder.build_messages.assert_not_called()
    invoice_reader.load.assert_called_once_with(excel_bytes=command.excel_bytes)
    invoice_reader.read_invoices.assert_called_once_with(worksheet_index=0)
    invoice_reader.unload.assert_called_once_with()


def test_execute_unloads_reader_and_propagates_selection_error(
    mocker: MockerFixture, invoice_factory, attachment_builder, email_sender
):
    command = CreateMailingListCommand(excel_bytes=b'excel content')
    invoices = [invoice_factory(None, None, None, None)]
    invoice_reader = mocker.create_autospec(
        InvoiceExcelReader, instance=True, spec_set=True
    )
    invoice_reader.read_invoices.return_value = invoices
    invoice_selector = mocker.create_autospec(
        MailingInvoiceSelector, instance=True, spec_set=True
    )
    selection_error = ValueError('Ошибка отбора счетов')
    invoice_selector.select_invoices.side_effect = selection_error
    mailing_list_builder = mocker.create_autospec(
        RecipientMailingListBuilder, instance=True, spec_set=True
    )
    message_builder = mocker.create_autospec(
        InvoiceMessageBuilder, instance=True, spec_set=True
    )
    interactor = CreateMailingListFromExcelInteractor(
        invoice_reader=invoice_reader,
        invoice_selector=invoice_selector,
        mailing_list_builder=mailing_list_builder,
        message_builder=message_builder,
        attachment_builder=attachment_builder,
        email_sender=email_sender,
    )

    with pytest.raises(ValueError) as error:
        interactor.execute(command=command)

    email_sender.send_email.assert_not_called()
    attachment_builder.build_attachment.assert_not_called()
    assert error.value is selection_error
    mailing_list_builder.build.assert_not_called()
    message_builder.build_messages.assert_not_called()
    invoice_selector.select_invoices.assert_called_once_with(invoices)
    invoice_reader.unload.assert_called_once_with()


@pytest.fixture
def attachment_builder(mocker):
    builder = mocker.create_autospec(
        InvoiceAttachmentBuilder, instance=True, spec_set=True
    )
    builder.build_attachment.return_value = EmailAttachment(
        filename='invoices.xlsx',
        content_type='application/test',
        content=b'xlsx content',
    )
    return builder


@pytest.fixture
def email_sender(mocker):
    return mocker.create_autospec(EmailSender, instance=True, spec_set=True)
