import pytest

from src.domain.entity.invoice_message import InvoiceMessage
from src.application.ports.employee_email_lookup import EmployeeEmailLookup
from src.domain.services.invoice_message_builder import InvoiceMessageBuilder


@pytest.fixture
def employee_email_lookup(mocker):
    return mocker.create_autospec(EmployeeEmailLookup, instance=True, spec_set=True)


def test_build_messages_keeps_email_recipients(employee_email_lookup, invoice_factory):
    invoices = [invoice_factory(invoice_number="INV-001")]
    builder = InvoiceMessageBuilder(employee_email_lookup)

    assert builder.build_messages({"department@example.com": invoices}) == [
        InvoiceMessage(recipient_email="department@example.com", invoices=invoices),
    ]
    employee_email_lookup.get_email.assert_not_called()


def test_build_messages_resolves_employee_identifier(employee_email_lookup, invoice_factory):
    invoices = [invoice_factory(invoice_number="INV-001")]
    employee_email_lookup.get_email.return_value = "employee@example.com"
    builder = InvoiceMessageBuilder(employee_email_lookup)

    assert builder.build_messages({"EMP-001": invoices}) == [
        InvoiceMessage(recipient_email="employee@example.com", invoices=invoices),
    ]
    employee_email_lookup.get_email.assert_called_once_with("EMP-001")


@pytest.mark.parametrize("resolved_email", [None, "", "not-an-email"])
def test_build_messages_skips_unresolved_addresses(employee_email_lookup, resolved_email):
    employee_email_lookup.get_email.return_value = resolved_email

    assert InvoiceMessageBuilder(employee_email_lookup).build_messages({"EMP-001": []}) == []


def test_build_messages_skips_missing_recipients(employee_email_lookup):
    assert InvoiceMessageBuilder(employee_email_lookup).build_messages({None: [], "": []}) == []
    employee_email_lookup.get_email.assert_not_called()


def test_build_messages_propagates_lookup_failure(employee_email_lookup):
    lookup_error = RuntimeError("Directory unavailable")
    employee_email_lookup.get_email.side_effect = lookup_error

    with pytest.raises(RuntimeError) as error:
        InvoiceMessageBuilder(employee_email_lookup).build_messages({"EMP-001": []})

    assert error.value is lookup_error
