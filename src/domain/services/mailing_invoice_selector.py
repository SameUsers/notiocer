from datetime import datetime, timedelta

from ..entity.invoice import Invoice


class MailingInvoiceSelector:
    def __init__(
        self, allowed_categories: set[str], minimum_invoice_age: timedelta
    ) -> None:
        self._allowed_categories = frozenset(allowed_categories)
        self._minimum_invoice_age = minimum_invoice_age

    def select_invoices(self, invoices: list[Invoice]) -> set[Invoice]:
        invoice_date_cutoff = datetime.now() - self._minimum_invoice_age
        return {
            invoice
            for invoice in invoices
            if invoice.category in self._allowed_categories
            and invoice.invoice_date is not None
            and invoice.invoice_date < invoice_date_cutoff
            and ((invoice.sign == 'да') or (invoice.payment_terms == 'До загрузки'))
        }
