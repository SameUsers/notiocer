from typing import Protocol

from ...domain.entity.invoice import Invoice


class InvoiceExcelReader(Protocol):
    def load(self, excel_bytes: bytes) -> None:
        ...

    def read_invoices(self, worksheet_index: int) -> list[Invoice]:
        """Read all data rows, preserving missing values for domain decisions."""
        ...

    def unload(self) -> None:
        ...
