from typing import Protocol

from notiocer.domain.models.invoice import Invoice


class InvoiceReader(Protocol):
    """Порт чтения счетов из Excel с циклом load → read_invoices → unload."""

    def load(self, report_content: bytes) -> None:
        """Загружает книгу из байтов Excel-файла."""
        ...

    def read_invoices(self, worksheet_index: int) -> list[Invoice]:
        """Читает счета с листа по его индексу, начиная с нуля."""
        ...

    def unload(self) -> None:
        """Освобождает загруженную книгу и связанные ресурсы."""
        ...
