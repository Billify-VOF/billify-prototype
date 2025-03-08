import pytest
from datetime import date, timedelta
from decimal import Decimal
from domain.models.invoice import Invoice
from domain.services.invoice_service import InvoiceService
from domain.models.value_objects import InvoiceStatus, UrgencyLevel

def test_create_invoice_valid():
    service = InvoiceService()
    data = {
        'amount': Decimal("100"),
        'due_date': date.today(),
        'invoice_number': "INV-001"
    }
    invoice = service.create(data)
    assert invoice.invoice_number == "INV-001"

def test_create_invoice_missing_field():
    service = InvoiceService()
    with pytest.raises(KeyError):
        service.create({'due_date': date.today()})

def test_update_method_return_value():
    service = InvoiceService()
    invoice = Invoice.create(
        amount=Decimal("100"),
        due_date=date.today(),
        invoice_number="INV-002"
    )
    updated = service.update(invoice, {
        'amount': Decimal("150"),
        'due_date': date.today() + timedelta(days=5)
    })
    assert updated is invoice

def test_update_statuses_overdue():
    service = InvoiceService()
    invoice = Invoice.create(
        amount=Decimal("100"),
        due_date=date.today() - timedelta(days=5),
        invoice_number="INV-003"
    )
    service.update_statuses([invoice])
    assert invoice.status == InvoiceStatus.OVERDUE

def test_update_status_non_overdue():
    service = InvoiceService()
    inv = Invoice.create(
        amount=Decimal("100"),
        due_date=date.today() + timedelta(days=5),
        invoice_number="INV-004"
    )
    service.update_statuses([inv])
    assert inv.status == InvoiceStatus.PENDING

def test_update_invalid_keys():
    service = InvoiceService()
    inv = Invoice.create(
        amount=Decimal("100"),
        due_date=date.today(),
        invoice_number="INV-005"
    )

    with pytest.raises(KeyError):
        service.update(inv, {"invalid_key": "value"})

def test_calculate_status_all_branches():
    service = InvoiceService()
    today = date.today()

    # Paid case
    paid_inv = Invoice.create(
        amount=Decimal("100"),
        due_date=today,
        invoice_number="INV-006",
        status=InvoiceStatus.PAID
    )
    assert service._calculate_status(paid_inv, today) == InvoiceStatus.PAID

    # Overdue case
    overdue_inv = Invoice.create(
        amount=Decimal("100"),
        due_date=today - timedelta(days=1),
        invoice_number="INV-007"
    )
    assert service._calculate_status(overdue_inv, today) == InvoiceStatus.OVERDUE

    # Pending case
    pending_inv = Invoice.create(
        amount=Decimal("100"),
        due_date=today + timedelta(days=7),
        invoice_number="INV-008"
    )
    assert service._calculate_status(pending_inv, today) == InvoiceStatus.PENDING

def test_get_urgency_info():
    service = InvoiceService()

    # Test manual urgency
    manual_inv = Invoice.create(
        amount=Decimal("200"),
        due_date=date.today(),
        invoice_number="INV-009"
    )
    manual_inv.set_urgency_manually(UrgencyLevel.HIGH)
    manual_info = service.get_urgency_info(manual_inv)
    assert manual_info['is_manual'] is True

    # Test automatic urgency
    auto_inv = Invoice.create(
        amount=Decimal("300"),
        due_date=date.today() + timedelta(days=20),
        invoice_number="INV-010"
    )
    auto_info = service.get_urgency_info(auto_inv)
    assert auto_info['is_manual'] is False
    assert auto_info['level'] == "MEDIUM"