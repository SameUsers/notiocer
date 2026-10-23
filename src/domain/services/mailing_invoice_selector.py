from datetime import datetime, timedelta

from ..entity.invoice import Invoice


class MailingInvoiceSelector:
    def select_invoices(self, invoices: list[Invoice]) -> set[Invoice]:
        cutoff = datetime.now() - timedelta(days=4)
        eligible_categories = {"Д0", "Д1", "Д2", "Д3", "Д4", "Д5", "Д60"}
        return {
            invoice
            for invoice in invoices
            if invoice.category in eligible_categories
            and invoice.invoice_date is not None
            and invoice.invoice_date < cutoff
            and (invoice.sign == "да" or invoice.payment_terms == "До загрузки")
        }
