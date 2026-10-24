from collections.abc import Sequence
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from src.application.dto.email_attachment import EmailAttachment
from src.domain.entity.invoice import Invoice

INVOICE_COLUMNS = (
    ('client_id', 'ID клиента'),
    ('legal_entity', 'Юр лицо'),
    ('subject', 'Счет на'),
    ('invoice_number', 'Полный номер счета'),
    ('invoice_date', 'Дата счета'),
    ('invoice_amount', 'Сумма счета'),
    ('balance', 'Сальдо'),
    ('currency', 'Валюта'),
    ('category', 'Категория'),
    ('payment_due_date', 'Срок оплаты'),
    ('sign', 'Предоплата до загрузки'),
    ('employee', 'Сотрудник'),
    ('equipment_service', 'Услуга отдела оборудования'),
    ('transport_reference', 'Номер контейнера / AWB /авто'),
    ('unloading_date', 'Дата выгрузки'),
    ('sfb_curator', 'Куратор СФБ'),
    ('shipping_date', 'Дата отгрузки'),
    ('estimated_arrival_date', 'Прогнозная ETA'),
    ('market', 'Рынок'),
    ('payment_service', 'Сервис для срока оплаты'),
    ('payment_terms_type', 'Тип платежных условий'),
    ('contract_details', '№ и дата договора'),
    ('service_type', 'Тип сервиса'),
    ('partial_prepayment', 'Частичная предоплата'),
    ('partial_prepayment_terms', 'Условия частичной предоплаты'),
    ('payment_terms', 'Крайний момент оплаты'),
    ('calculated_payment_term', 'Расчетный с/о'),
)


class OpenpyxlInvoiceAttachmentBuilder:
    """Builds an ``.xlsx`` email attachment from a list of invoices.

    Produces a single-sheet workbook with a styled header row and one
    data row per invoice, using the column layout defined in
    :data:`INVOICE_COLUMNS`.
    """

    def _style_headers(self, worksheet: Worksheet) -> None:
        """Apply header styling to the first row of the worksheet.

        Sets a solid fill, bold white font, centered wrapped alignment,
        thin borders, fixed column widths, and a taller header row.

        Args:
            worksheet: Worksheet whose header row should be styled.
        """
        header_fill = PatternFill(
            fill_type='solid',
            fgColor='1F4E78',
        )

        header_font = Font(
            name='Calibri',
            size=11,
            bold=True,
            color='FFFFFF',
        )

        header_alignment = Alignment(
            horizontal='center',
            vertical='center',
            wrap_text=True,
        )

        border_side = Side(
            style='thin',
            color='D9E2F3',
        )

        for column_index, cell in enumerate(worksheet[1], start=1):
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = Border(
                left=border_side,
                right=border_side,
                top=border_side,
                bottom=border_side,
            )

            column_letter = get_column_letter(column_index)

            worksheet.column_dimensions[column_letter].width = 22

        worksheet.row_dimensions[1].height = 40

    def build_attachment(self, invoices: Sequence[Invoice]) -> EmailAttachment:
        """Build an ``.xlsx`` attachment containing the given invoices.

        Args:
            invoices: Invoices to write into the attachment.

        Returns:
            An email attachment with the generated workbook content.

        Raises:
            RuntimeError: If the workbook has no active worksheet.
        """
        workbook = Workbook()
        try:
            worksheet = workbook.active
            if worksheet is None:
                raise RuntimeError('Не удалось создать лист для вложения')
            worksheet.title = 'Счета'
            worksheet.append([header for _, header in INVOICE_COLUMNS])
            self._style_headers(worksheet)
            for invoice in invoices:
                worksheet.append(
                    [getattr(invoice, field_name) for field_name, _ in INVOICE_COLUMNS]
                )
            with BytesIO() as excel_buffer:
                workbook.save(excel_buffer)
                content = excel_buffer.getvalue()
        finally:
            workbook.close()
        return EmailAttachment(
            filename='invoices.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            content=content,
        )
