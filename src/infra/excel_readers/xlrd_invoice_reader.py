from collections.abc import Sequence
from typing import Any

from xlrd import (
    XL_CELL_BLANK,
    XL_CELL_DATE,
    XL_CELL_EMPTY,
    Book,
    open_workbook,
    xldate_as_datetime,
)
from xlrd.sheet import Cell

from src.domain.entity.invoice import Invoice


class XlrdInvoiceReader:
    def __init__(self) -> None:
        self._workbook: Book | None = None

    def load(self, excel_bytes: bytes) -> None:
        if self._workbook is not None:
            raise RuntimeError('Файл уже был загружен. Сначала вызовите unload()')
        self._workbook = open_workbook(file_contents=excel_bytes)

    def unload(self) -> None:
        if self._workbook is not None:
            self._workbook.release_resources()
            self._workbook = None

    def read_invoices(self, worksheet_index: int) -> list[Invoice]:
        row_count = self._get_row_count(worksheet_index=worksheet_index)
        headers = self._read_headers(worksheet_index=worksheet_index)
        invoice_rows = [
            dict(
                zip(
                    headers,
                    self._read_row(
                        row_index=row_index, worksheet_index=worksheet_index
                    ),
                )
            )
            for row_index in range(1, row_count)
        ]
        return [self._map_row_to_invoice(row_values) for row_values in invoice_rows]

    def _read_headers(self, worksheet_index: int) -> Sequence[Any]:
        return self._read_row(row_index=0, worksheet_index=worksheet_index)

    def _get_row_count(self, worksheet_index: int) -> int:
        worksheet = self.workbook.sheet_by_index(worksheet_index)
        return worksheet.nrows

    def _read_row(self, row_index: int, worksheet_index: int) -> Sequence[Any]:
        worksheet = self.workbook.sheet_by_index(worksheet_index)
        return [self._read_cell_value(cell) for cell in worksheet.row(row_index)]

    def _read_cell_value(self, cell: Cell) -> Any:
        if cell.ctype in (XL_CELL_EMPTY, XL_CELL_BLANK):
            return None
        if cell.ctype == XL_CELL_DATE:
            return xldate_as_datetime(cell.value, self.workbook.datemode)  # type: ignore
        return cell.value

    def _map_row_to_invoice(self, row_values: dict[str, Any]) -> Invoice:
        return Invoice(
            client_id=row_values.get('ID клиента'),
            legal_entity=row_values.get('Юр лицо'),
            subject=row_values.get('Счет на'),
            invoice_number=row_values.get('Полный номер счета'),
            invoice_date=row_values.get('Дата счета'),
            invoice_amount=row_values.get('Сумма счета'),
            balance=row_values.get('Сальдо'),
            currency=row_values.get('Валюта'),
            category=row_values.get('Категория'),
            payment_due_date=row_values.get('Срок оплаты'),
            sign=row_values.get('Предоплата до загрузки'),
            employee=row_values.get('Сотрудник'),
            equipment_service=row_values.get('Услуга отдела оборудования'),
            transport_reference=row_values.get('Номер контейнера / AWB /авто'),
            unloading_date=row_values.get('Дата выгрузки'),
            sfb_curator=row_values.get('Куратор СФБ'),
            shipping_date=row_values.get('Дата отгрузки'),
            estimated_arrival_date=row_values.get('Прогнозная ETA'),
            market=row_values.get('Рынок'),
            payment_service=row_values.get('Сервис для срока оплаты'),
            payment_terms_type=row_values.get('Тип платежных условий'),
            contract_details=row_values.get('№ и дата договора'),
            service_type=row_values.get('Тип сервиса'),
            partial_prepayment=row_values.get('Частичная предоплата'),
            partial_prepayment_terms=row_values.get('Условия частичной предоплаты'),
            payment_terms=row_values.get('Крайний момент оплаты'),
            calculated_payment_term=row_values.get('Расчетный с/о'),
        )

    @property
    def workbook(self) -> Book:
        if self._workbook is None:
            raise ValueError('Файл не был загружен')
        return self._workbook
