from datetime import datetime

import pytest
from xlrd import XL_CELL_DATE, XL_CELL_EMPTY, XL_CELL_TEXT
from xlrd.sheet import Cell

from src.infra.excel_readers.xlrd_invoice_reader import XlrdInvoiceReader


@pytest.fixture
def workbook(mocker):
    headers = [
        "Категория", "Крайний момент оплаты", "Дата счета", "Предоплата до загрузки",
        "Полный номер счета", "Счет на", "Юр лицо", "Сервис для срока оплаты", "Рынок", "Сотрудник",
    ]
    header_cells = [Cell(XL_CELL_TEXT, header) for header in headers]
    invoice_cells = [
        Cell(XL_CELL_TEXT, "Д0"), Cell(XL_CELL_TEXT, "До загрузки"),
        Cell(XL_CELL_DATE, 45292), Cell(XL_CELL_TEXT, "да"),
        Cell(XL_CELL_TEXT, "INV-001"), Cell(XL_CELL_TEXT, "Перевозка"), Cell(XL_CELL_EMPTY, ""),
        Cell(XL_CELL_TEXT, "Отдел перевозок"),
        Cell(XL_CELL_TEXT, "РБ"), Cell(XL_CELL_TEXT, "employee@example.com"),
    ]
    first_sheet = mocker.Mock(nrows=1)
    first_sheet.row.side_effect = [header_cells].__getitem__
    second_sheet = mocker.Mock(nrows=3)
    second_sheet.row.side_effect = [header_cells, invoice_cells, [Cell(XL_CELL_EMPTY, "")] * len(headers)].__getitem__
    workbook = mocker.Mock(datemode=0)
    workbook.sheet_by_index.side_effect = [first_sheet, second_sheet].__getitem__
    mocker.patch("src.infra.excel_readers.xlrd_invoice_reader.open_workbook", return_value=workbook)
    return workbook


def test_read_invoices_uses_selected_sheet_and_normalizes_cells(workbook, invoice_factory):
    reader = XlrdInvoiceReader()
    reader.load(b"xls content")

    assert reader.read_invoices(worksheet_index=1) == [
        invoice_factory(
            category="Д0", payment_terms="До загрузки", invoice_date=datetime(2024, 1, 1),
            sign="да", invoice_number="INV-001", subject="Перевозка",
            payment_service="Отдел перевозок",
            market="РБ", employee="employee@example.com",
        ),
        invoice_factory(),
    ]


def test_read_invoices_returns_empty_list_for_headers_only(workbook):
    reader = XlrdInvoiceReader()
    reader.load(b"xls content")
    assert reader.read_invoices(worksheet_index=0) == []


def test_load_rejects_already_loaded_workbook(workbook):
    reader = XlrdInvoiceReader()
    reader.load(b"xls content")
    with pytest.raises(RuntimeError):
        reader.load(b"xls content")


def test_read_invoices_requires_loaded_workbook():
    with pytest.raises(ValueError):
        XlrdInvoiceReader().read_invoices(worksheet_index=0)


def test_unload_releases_resources_and_allows_reload(workbook):
    reader = XlrdInvoiceReader()
    reader.load(b"xls content")
    reader.unload()
    workbook.release_resources.assert_called_once_with()
    with pytest.raises(ValueError):
        _ = reader.workbook
    reader.unload()
    workbook.release_resources.assert_called_once_with()
    reader.load(b"xls content")
    assert reader.workbook is workbook


@pytest.mark.parametrize("datemode, expected_date", [(0, datetime(2024, 1, 1)), (1, datetime(2028, 1, 2))])
def test_read_invoices_uses_workbook_date_system(workbook, datemode, expected_date):
    workbook.datemode = datemode
    reader = XlrdInvoiceReader()
    reader.load(b"xls content")
    assert reader.read_invoices(worksheet_index=1)[0].invoice_date == expected_date
