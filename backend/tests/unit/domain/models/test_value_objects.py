import pytest
from domain.models.value_objects import UrgencyLevel, InvoiceStatus

@pytest.mark.parametrize("days,urgency_level", [
    (-5, UrgencyLevel.OVERDUE),
    (3, UrgencyLevel.CRITICAL),
    (10, UrgencyLevel.HIGH),
    (20, UrgencyLevel.MEDIUM),
    (40, UrgencyLevel.LOW)
])
def test_urgency_calculation(days, urgency_level: UrgencyLevel):
    assert UrgencyLevel.calculate_from_days(days) == urgency_level

@pytest.mark.parametrize("day_range,urgency_level", [
    ((None, -1), UrgencyLevel.OVERDUE),
    ((0, 7), UrgencyLevel.CRITICAL),
    ((8, 14), UrgencyLevel.HIGH),
    ((15, 30), UrgencyLevel.MEDIUM),
    ((31, None), UrgencyLevel.LOW)
])
def test_urgency_day_range(day_range, urgency_level: UrgencyLevel):
    assert urgency_level.day_range == day_range

@pytest.mark.parametrize("db_value,urgency_level", [
    (1, UrgencyLevel.OVERDUE),
    (2, UrgencyLevel.CRITICAL),
    (3, UrgencyLevel.HIGH),
    (4, UrgencyLevel.MEDIUM),
    (5, UrgencyLevel.LOW)
])
def test_urgency_from_db_value(db_value, urgency_level: UrgencyLevel):
    assert UrgencyLevel.from_db_value(db_value) == urgency_level

def test_urgency_from_db_value_invalid():
    with pytest.raises(ValueError):
        UrgencyLevel.from_db_value(6)

def test_urgency_choices():
    assert UrgencyLevel.choices() == [
        (1, "Overdue"),
        (2, "Critical"),
        (3, "High"),
        (4, "Medium"),
        (5, "Low")
    ]

@pytest.mark.parametrize("display_name,invoice_status", [
    ("Pending Payment", InvoiceStatus.PENDING),
    ("Payment Received", InvoiceStatus.PAID),
    ("Payment Overdue", InvoiceStatus.OVERDUE)
])
def test_invoice_status_display_names(display_name, invoice_status: InvoiceStatus):
    assert invoice_status.display_name == display_name

def test_invoice_status_choices():
    assert InvoiceStatus.choices() == [
        ("pending", "Pending Payment"),
        ("paid", "Payment Received"),
        ("overdue", "Payment Overdue")
    ]

@pytest.mark.parametrize("db_value,invoice_status", [
    ("pending", InvoiceStatus.PENDING),
    ("paid", InvoiceStatus.PAID),
    ("overdue", InvoiceStatus.OVERDUE)
])
def test_invoice_status_from_db_value(db_value, invoice_status: InvoiceStatus):
    assert InvoiceStatus.from_db_value(db_value) == invoice_status

def test_invoice_status_from_db_value_invalid():
    with pytest.raises(ValueError):
        InvoiceStatus.from_db_value('invalid')