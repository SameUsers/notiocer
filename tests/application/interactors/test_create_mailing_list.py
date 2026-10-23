from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.interactors.create_mailing_list import CreateMailingListInteractor
from src.application.ports.invoice_excel_reader import InvoiceExcelReader
from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector


def test_execute_returns_selected_invoices_and_unloads_reader(mocker: MockerFixture, invoice_factory):
    command = CreateMailingListCommand(excel_bytes=b"excel content")
    invoices = [
        invoice_factory(
            category="Предоплата",
            payment_terms="До загрузки",
            invoice_date=datetime(2000, 10, 1),
            sign="да",
        ),
        invoice_factory(None, None, None, None),
    ]
    invoice_reader = mocker.create_autospec(InvoiceExcelReader, instance=True, spec_set=True)
    invoice_reader.read_invoices.return_value = invoices
    selected_invoices = {invoices[0]}
    invoice_selector = mocker.create_autospec(MailingInvoiceSelector, instance=True, spec_set=True)
    invoice_selector.select_invoices.return_value = selected_invoices
    interactor = CreateMailingListInteractor(invoice_reader=invoice_reader, invoice_selector=invoice_selector)

    result = interactor.execute(command=command)

    assert result == selected_invoices
    invoice_selector.select_invoices.assert_called_once_with(invoices)
    invoice_reader.load.assert_called_once_with(excel_bytes=command.excel_bytes)
    invoice_reader.read_invoices.assert_called_once_with(worksheet_index=0)
    invoice_reader.unload.assert_called_once_with()


def test_execute_unloads_reader_and_propagates_read_error(mocker: MockerFixture):
    command = CreateMailingListCommand(excel_bytes=b"excel content")
    invoice_reader = mocker.create_autospec(InvoiceExcelReader, instance=True, spec_set=True)
    read_error = ValueError("Ошибка чтения счетов")
    invoice_reader.read_invoices.side_effect = read_error
    invoice_selector = mocker.create_autospec(MailingInvoiceSelector, instance=True, spec_set=True)
    interactor = CreateMailingListInteractor(invoice_reader=invoice_reader, invoice_selector=invoice_selector)

    with pytest.raises(ValueError) as error:
        interactor.execute(command=command)

    assert error.value is read_error
    invoice_selector.select_invoices.assert_not_called()
    invoice_reader.load.assert_called_once_with(excel_bytes=command.excel_bytes)
    invoice_reader.read_invoices.assert_called_once_with(worksheet_index=0)
    invoice_reader.unload.assert_called_once_with()


def test_execute_unloads_reader_and_propagates_selection_error(mocker: MockerFixture, invoice_factory):
    command = CreateMailingListCommand(excel_bytes=b"excel content")
    invoices = [invoice_factory(None, None, None, None)]
    invoice_reader = mocker.create_autospec(InvoiceExcelReader, instance=True, spec_set=True)
    invoice_reader.read_invoices.return_value = invoices
    invoice_selector = mocker.create_autospec(MailingInvoiceSelector, instance=True, spec_set=True)
    selection_error = ValueError("Ошибка отбора счетов")
    invoice_selector.select_invoices.side_effect = selection_error
    interactor = CreateMailingListInteractor(invoice_reader=invoice_reader, invoice_selector=invoice_selector)

    with pytest.raises(ValueError) as error:
        interactor.execute(command=command)

    assert error.value is selection_error
    invoice_selector.select_invoices.assert_called_once_with(invoices)
    invoice_reader.unload.assert_called_once_with()
