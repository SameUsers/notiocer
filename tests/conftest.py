import pytest

from src.domain.entity.invoice import Invoice


@pytest.fixture
def invoice_factory():
    def make_invoice(
        category=None,
        payment_terms=None,
        invoice_date=None,
        sign=None,
        legal_entity=None,
        subject=None,
        invoice_number=None,
    ) -> Invoice:
        return Invoice(
            category=category,
            payment_terms=payment_terms,
            invoice_date=invoice_date,
            sign=sign,
            legal_entity=legal_entity,
            subject=subject,
            invoice_number=invoice_number,
        )

    return make_invoice
