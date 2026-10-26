from datetime import datetime, timedelta

from notiocer.domain.models.invoice import Invoice


class MailingInvoiceSelector:
    """Отбирает счета по категории, возрасту и условиям оплаты."""

    def __init__(
        self, allowed_categories: set[str], minimum_invoice_age: timedelta
    ) -> None:
        """Принимает разрешённые категории и минимальный возраст счёта."""
        self._allowed_categories = frozenset(allowed_categories)
        self._minimum_invoice_age = minimum_invoice_age

    def select_invoices(self, invoices: list[Invoice]) -> set[Invoice]:
        """Возвращает уникальные счета старше порога с предоплатой или оплатой до загрузки."""
        invoice_date_cutoff = datetime.now() - self._minimum_invoice_age
        return {
            invoice
            for invoice in invoices
            if invoice.category in self._allowed_categories
            and invoice.invoice_date is not None
            and invoice.invoice_date < invoice_date_cutoff
            and (
                (invoice.prepayment_before_loading == 'да')
                or (invoice.payment_milestone == 'До загрузки')
            )
        }
