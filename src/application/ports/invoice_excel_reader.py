from typing import Protocol

from ...domain.entity.invoice import Invoice


class InvoiceExcelReader(Protocol):
    """Протокол для чтения счетов из книги Excel.

    Ожидается, что реализации будут следовать трёхшаговому жизненному циклу:
    загрузить байты книги с помощью :meth:`load`, прочитать счета с
    конкретного листа с помощью :meth:`read_invoices` и освободить
    ресурсы с помощью :meth:`unload`.
    """

    def load(self, excel_bytes: bytes) -> None:
        """Загружает книгу Excel из сырых байтов в память.

        Args:
            excel_bytes: Сырое содержимое файла ``.xlsx``, который нужно разобрать.
        """
        ...

    def read_invoices(self, worksheet_index: int) -> list[Invoice]:
        """Читает счета с листа загруженной книги.

        Args:
            worksheet_index: Индекс листа (начиная с нуля) для чтения.

        Returns:
            Список счетов, разобранных с указанного листа.
        """
        ...

    def unload(self) -> None:
        """Освобождает загруженную книгу и связанные с ней ресурсы."""
        ...
