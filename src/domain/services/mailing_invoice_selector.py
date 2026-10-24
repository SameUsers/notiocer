from datetime import datetime, timedelta

from ..entity.invoice import Invoice


class MailingInvoiceSelector:
    """Отбирает счета, подходящие для списка рассылки.

    Счёт отбирается, когда его категория разрешена, дата выставления счёта
    старше настроенного минимального возраста и он соответствует одному из
    условий оплаты (подписан или оплата до загрузки).
    """

    def __init__(
        self, allowed_categories: set[str], minimum_invoice_age: timedelta
    ) -> None:
        """Инициализирует селектор.

        Args:
            allowed_categories: Категории счетов, подходящих для рассылки.
            minimum_invoice_age: Минимальный возраст счёта, необходимый для его отбора.
        """
        self._allowed_categories = frozenset(allowed_categories)
        self._minimum_invoice_age = minimum_invoice_age

    def select_invoices(self, invoices: list[Invoice]) -> set[Invoice]:
        """Отбирает счета, подходящие для списка рассылки.

        Args:
            invoices: Счета-кандидаты для фильтрации.

        Returns:
            Подмножество счетов, удовлетворяющих всем критериям отбора.
        """
        invoice_date_cutoff = datetime.now() - self._minimum_invoice_age
        return {
            invoice
            for invoice in invoices
            if invoice.category in self._allowed_categories
            and invoice.invoice_date is not None
            and invoice.invoice_date < invoice_date_cutoff
            and ((invoice.sign == 'да') or (invoice.payment_terms == 'До загрузки'))
        }
