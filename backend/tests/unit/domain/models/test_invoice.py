import pytest
from datetime import date, timedelta
from decimal import Decimal
from domain.models.invoice import Invoice
from domain.models.value_objects import InvoiceStatus, UrgencyLevel
from domain.exceptions import InvalidInvoiceError


def test_create_valid_invoice():
    invoice = Invoice.create(
        amount=Decimal("100.50"),
        due_date=date.today() + timedelta(days=10),
        invoice_number="INV-001"
    )

    assert invoice.amount == Decimal("100.50")
    assert invoice.status == InvoiceStatus.PENDING

def test_create_invalid_negative_amount():
    with pytest.raises(InvalidInvoiceError):
        Invoice.create(
            amount=Decimal("-50"),
            due_date=date.today(),
            invoice_number="INV-002"
        )

def test_mark_as_paid():
    invoice = Invoice.create(
        amount=Decimal("200"),
        due_date=date.today(),
        invoice_number="INV-003"
    )

    invoice.mark_as_paid()

    assert invoice.status == InvoiceStatus.PAID
    assert invoice.is_paid is True

def test_urgency_calculation():
    invoice = Invoice.create(
        amount=Decimal("300"),
        due_date=date.today() + timedelta(days=3),
        invoice_number="INV-004"
    )

    assert invoice.urgency == UrgencyLevel.CRITICAL

def test_set_urgency_invalid_type():
    invoice = Invoice.create(
        amount=Decimal("200"),
        due_date=date.today(),
        invoice_number="INV-005"
    )

    with pytest.raises(InvalidInvoiceError):
        invoice.set_urgency_manually("invalid")

    with pytest.raises(InvalidInvoiceError):
        invoice.update(manual_urgency="invalid")

def test_set_manual_urgency():
    invoice = Invoice.create(
        amount=Decimal("400"),
        due_date=date.today() + timedelta(days=20),
        invoice_number="INV-006"
    )

    invoice.set_urgency_manually(UrgencyLevel.HIGH)
    assert invoice.urgency == UrgencyLevel.HIGH
    assert invoice.is_urgency_manually_set() is True

    invoice.clear_manual_urgency()
    assert invoice.is_urgency_manually_set() is False

def test_update_manual_urgency():
    invoice = Invoice.create(
        amount=Decimal("400"),
        due_date=date.today(),
        invoice_number="INV-007"
    )

    invoice.update(manual_urgency=UrgencyLevel.CRITICAL)
    assert invoice.urgency == UrgencyLevel.CRITICAL

    invoice.update(manual_urgency=False)
    assert invoice.is_urgency_manually_set() is False

def test_validate_status_invalid_type():
    invoice = Invoice.create(
        amount=Decimal("100"),
        due_date=date.today(),
        invoice_number="INV-008"
    )
    invoice.status = "invalid"
    with pytest.raises(InvalidInvoiceError):
        invoice.validate_status()

def test_get_status_display():
    invoice = Invoice.create(
        amount=Decimal("100"),
        due_date=date.today(),
        invoice_number="INV-009",
        status=InvoiceStatus.OVERDUE
    )
    assert invoice.get_status_display() == "Payment Overdue"

def test_validate_status_overdue_with_future_date():
    with pytest.raises(InvalidInvoiceError):
        Invoice.create(
            amount=Decimal("100"),
            due_date=date.today() + timedelta(days=5),
            invoice_number="INV-010",
            status=InvoiceStatus.OVERDUE
        )

def test_update_individual_fields():
    invoice = Invoice.create(
        amount=Decimal("300"),
        due_date=date.today(),
        invoice_number="INV-011"
    )

    invoice.update(amount=Decimal("350"))
    assert invoice.amount == Decimal("350")

    new_date = date.today() + timedelta(days=10)
    invoice.update(due_date=new_date)
    assert invoice.due_date == new_date

    invoice.update(invoice_number="INV-011A")
    assert invoice.invoice_number == "INV-011A"

    invoice.update(status=InvoiceStatus.PAID)
    assert invoice.status == InvoiceStatus.PAID