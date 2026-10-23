from datetime import datetime, timedelta

import pytest

from src.domain.services.mailing_invoice_selector import MailingInvoiceSelector


@pytest.fixture
def invoice_selector():
    return MailingInvoiceSelector(
        allowed_categories={"Д0", "Д1", "Д2", "Д3", "Д4", "Д5", "Д60"},
        minimum_invoice_age=timedelta(days=4),
    )


@pytest.fixture
def current_time(mocker):
    current_time = datetime(2026, 10, 22, 12)
    clock = mocker.patch(
        "src.domain.services.mailing_invoice_selector.datetime", wraps=datetime,
    )
    clock.now.return_value = current_time
    return current_time


@pytest.mark.parametrize("category", ["Д0", "Д1", "Д2", "Д3", "Д4", "Д5", "Д60"])
def test_select_invoices_accepts_eligible_categories(invoice_factory, current_time, category, invoice_selector):
    invoice = invoice_factory(
        category=category, invoice_date=current_time - timedelta(days=5), sign="да",
    )

    assert invoice_selector.select_invoices([invoice]) == {invoice}


@pytest.mark.parametrize(
    ("sign", "payment_terms", "is_selected"),
    [
        ("да", None, True),
        (None, "До загрузки", True),
        ("да", "До загрузки", True),
        ("нет", "После загрузки", False),
        (None, None, False),
    ],
)
def test_select_invoices_accepts_either_selection_condition(
    invoice_factory, current_time, sign, payment_terms, is_selected,
    invoice_selector,
):
    invoice = invoice_factory(
        category="Д0", invoice_date=current_time - timedelta(days=5),
        sign=sign, payment_terms=payment_terms,
    )

    assert invoice_selector.select_invoices([invoice]) == ({invoice} if is_selected else set())


@pytest.mark.parametrize(
    ("invoice_age", "is_selected"),
    [
        (timedelta(days=4, microseconds=1), True),
        (timedelta(days=4), False),
        (timedelta(days=4) - timedelta(microseconds=1), False),
        (timedelta(days=-1), False),
    ],
)
def test_select_invoices_respects_four_day_boundary(
    invoice_factory, current_time, invoice_age, is_selected,
    invoice_selector,
):
    invoice = invoice_factory(category="Д0", invoice_date=current_time - invoice_age, sign="да")

    assert invoice_selector.select_invoices([invoice]) == ({invoice} if is_selected else set())


@pytest.mark.parametrize("category", [None, "Д6", "НДЗ"])
def test_select_invoices_rejects_other_categories(invoice_factory, current_time, category, invoice_selector):
    invoice = invoice_factory(
        category=category, invoice_date=current_time - timedelta(days=5),
        sign="да", payment_terms="До загрузки",
    )

    assert invoice_selector.select_invoices([invoice]) == set()


def test_select_invoices_rejects_missing_date(invoice_factory, current_time, invoice_selector):
    invoice = invoice_factory(category="Д0", sign="да", payment_terms="До загрузки")

    assert invoice_selector.select_invoices([invoice]) == set()


def test_select_invoices_removes_duplicates(invoice_factory, current_time, invoice_selector):
    invoice = invoice_factory(
        category="Д0", invoice_date=current_time - timedelta(days=5),
        sign="да", payment_terms="До загрузки", invoice_number="INV-001",
    )
    duplicate = invoice_factory(
        category="Д0", invoice_date=current_time - timedelta(days=5),
        sign="да", payment_terms="До загрузки", invoice_number="INV-001",
    )

    assert invoice_selector.select_invoices([invoice, duplicate]) == {invoice}


def test_select_invoices_accepts_empty_input(current_time, invoice_selector):
    assert invoice_selector.select_invoices([]) == set()


def test_select_invoices_uses_configured_age_and_categories(invoice_factory, current_time):
    selector = MailingInvoiceSelector(allowed_categories={"Особая"}, minimum_invoice_age=timedelta(days=2))
    invoice = invoice_factory(category="Особая", invoice_date=current_time - timedelta(days=3), sign="да")

    assert selector.select_invoices([invoice]) == {invoice}
