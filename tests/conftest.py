from dataclasses import fields

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
        payment_service=None,
        market=None,
        employee=None,
        **invoice_fields,
    ) -> Invoice:
        values = {field.name: None for field in fields(Invoice)}
        values.update(
            category=category,
            payment_terms=payment_terms,
            invoice_date=invoice_date,
            sign=sign,
            legal_entity=legal_entity,
            subject=subject,
            invoice_number=invoice_number,
            payment_service=payment_service,
            market=market,
            employee=employee,
        )
        values.update(invoice_fields)
        return Invoice(**values)

    return make_invoice
