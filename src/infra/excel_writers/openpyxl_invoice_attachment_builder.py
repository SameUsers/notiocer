from collections.abc import Sequence
from dataclasses import fields
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from src.application.dto.email_attachment import EmailAttachment
from src.domain.entity.invoice import Invoice


class OpenpyxlInvoiceAttachmentBuilder:
    """Формирует ``.xlsx``-вложение из списка счетов.

    Создаёт книгу с одним листом, стилизованной строкой заголовков
    и одной строкой данных на каждый счёт. Заголовки колонок берутся
    из метаданных ``Annotated`` полей :class:`Invoice`.
    """

    def _style_headers(self, worksheet: Worksheet) -> None:
        """Применяет стиль к строке заголовков.

        Задаёт сплошную заливку, жирный белый шрифт, центрированное
        выравнивание с переносом, тонкие границы, фиксированную ширину
        колонок и увеличенную высоту строки заголовков.

        Args:
            worksheet: Лист, строку заголовков которого нужно стилизовать.
        """
        header_fill = PatternFill(fill_type='solid', fgColor='1F4E78')
        header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        border_side = Side(style='thin', color='D9E2F3')

        for column_index, cell in enumerate(worksheet[1], start=1):
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = Border(
                left=border_side, right=border_side,
                top=border_side, bottom=border_side,
            )
            column_letter = get_column_letter(column_index)
            worksheet.column_dimensions[column_letter].width = 22

        worksheet.row_dimensions[1].height = 40

    @staticmethod
    def _column_title(field_info: Any) -> str:
        """Возвращает человекочитаемый заголовок колонки из меты ``Annotated``.

        Если у поля есть метаданные ``Annotated`` — берётся первая строка.
        Иначе используется имя поля.
        """
        metadata = getattr(field_info, 'metadata', ())
        if metadata:
            return str(metadata[0])
        return field_info.name

    def build_attachment(self, invoices: Sequence[Invoice]) -> EmailAttachment:
        """Формирует ``.xlsx``-вложение с указанными счетами.

        Args:
            invoices: Счета, которые нужно записать во вложение.

        Returns:
            Email-вложение с содержимым сформированной книги.

        Raises:
            RuntimeError: Если у книги нет активного листа.
        """
        invoice_fields = fields(Invoice)
        workbook = Workbook()
        try:
            worksheet = workbook.active
            if worksheet is None:
                raise RuntimeError('Не удалось создать лист для вложения')
            worksheet.title = 'Счета'

            worksheet.append([self._column_title(f) for f in invoice_fields])
            self._style_headers(worksheet)

            field_names = [f.name for f in invoice_fields]
            for invoice in invoices:
                worksheet.append([getattr(invoice, name) for name in field_names])

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