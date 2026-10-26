from collections.abc import Sequence
from io import BytesIO
from typing import Any

from openpyxl import Workbook, load_workbook

from notiocer.domain.models.invoice import Invoice


class OpenpyxlInvoiceReader:
    """Читает счета из XLSX через openpyxl с циклом load → read_invoices → unload."""

    def __init__(self) -> None:
        """Создаёт reader без загруженной книги."""
        self._workbook: Workbook | None = None

    def load(self, report_content: bytes) -> None:
        """Загружает книгу из байтов Excel-файла.

        Raises:
            RuntimeError: Предыдущая книга ещё не освобождена.
        """
        if self._workbook is not None:
            raise RuntimeError('Файл уже был загружен. Сначала вызовите unload()')
        self._workbook = load_workbook(filename=BytesIO(report_content), data_only=True)

    def _map_row_to_invoice(self, values_by_header: dict[str, Any]) -> Invoice:
        """Сопоставляет значения строки с полями счёта по заголовкам."""
        return Invoice(
            client_id=values_by_header.get('ID клиента'),
            legal_entity=values_by_header.get('Юр лицо'),
            billing_subject=values_by_header.get('Счет на'),
            invoice_number=values_by_header.get('Полный номер счета'),
            invoice_date=values_by_header.get('Дата счета'),
            invoice_amount=values_by_header.get('Сумма счета'),
            balance=values_by_header.get('Сальдо'),
            currency=values_by_header.get('Валюта'),
            category=values_by_header.get('Категория'),
            payment_due_date=values_by_header.get('Срок оплаты'),
            prepayment_before_loading=values_by_header.get('Предоплата до загрузки'),
            employee_id=values_by_header.get('Сотрудник'),
            equipment_service=values_by_header.get('Услуга отдела оборудования'),
            transport_reference=values_by_header.get('Номер контейнера / AWB /авто'),
            unloading_date=values_by_header.get('Дата выгрузки'),
            sfb_curator=values_by_header.get('Куратор СФБ'),
            shipping_date=values_by_header.get('Дата отгрузки'),
            estimated_arrival_date=values_by_header.get('Прогнозная ETA'),
            market=values_by_header.get('Рынок'),
            payment_service=values_by_header.get('Сервис для срока оплаты'),
            payment_terms_type=values_by_header.get('Тип платежных условий'),
            contract_details=values_by_header.get('№ и дата договора'),
            service_type=values_by_header.get('Тип сервиса'),
            partial_prepayment=values_by_header.get('Частичная предоплата'),
            partial_prepayment_terms=values_by_header.get(
                'Условия частичной предоплаты'
            ),
            payment_milestone=values_by_header.get('Крайний момент оплаты'),
            calculated_payment_term=values_by_header.get('Расчетный с/о'),
        )

    def _read_headers(self, worksheet_index: int) -> Sequence[Any]:
        """Читает первую строку листа как заголовки."""
        return self._read_row(row_index=0, worksheet_index=worksheet_index)

    def _read_row(self, row_index: int, worksheet_index: int) -> Sequence[Any]:
        """Читает строку по индексам строки и листа, начиная с нуля."""
        worksheet = self.workbook.worksheets[worksheet_index]
        return [cell.value for cell in worksheet[row_index + 1]]

    def _get_row_count(self, worksheet_index: int) -> int:
        """Возвращает количество строк на листе."""
        worksheet = self.workbook.worksheets[worksheet_index]
        return worksheet.max_row

    def read_invoices(self, worksheet_index: int) -> list[Invoice]:
        """Преобразует строки после заголовка в счета без бизнес-фильтрации."""
        row_count = self._get_row_count(worksheet_index=worksheet_index)
        headers = self._read_headers(worksheet_index=worksheet_index)
        rows_by_header = [
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
        return [
            self._map_row_to_invoice(values_by_header)
            for values_by_header in rows_by_header
        ]

    def unload(self) -> None:
        """Освобождает загруженную книгу и сбрасывает состояние reader."""
        if self._workbook is not None:
            self._workbook.close()
            self._workbook = None

    @property
    def workbook(self) -> Workbook:
        """Возвращает загруженную книгу.

        Raises:
            ValueError: Книга ещё не загружена.
        """
        if self._workbook is None:
            raise ValueError('Файл не был загружен')
        return self._workbook
