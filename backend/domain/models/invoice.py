"""Domain model representing an invoice and its business rules."""

from decimal import Decimal
from datetime import date
from typing import Optional
from domain.exceptions import InvalidInvoiceError


class Invoice:
    """
    Represents an invoice in our system, containing all relevant
    business data and validation rules.
    """

    def __init__(
        self,
        amount: Decimal,
        due_date: date,
        invoice_number: str,
        file_path: str,
        invoice_id: Optional[int] = None
    ):
        self.id = invoice_id
        self.amount = amount
        self.due_date = due_date
        self.invoice_number = invoice_number
        self.file_path = file_path
        self.status = 'pending'

    def validate(self):
        """Apply business rules to validate invoice data."""
        if self.amount <= 0:
            raise InvalidInvoiceError("Invoice amount must be positive")
        if self.due_date < date.today():
            raise InvalidInvoiceError("Due date cannot be in the past")

    def get_status_display(self) -> str:
        """Return a human-readable status description."""
        statuses = {
            'pending': 'Pending Payment',
            'paid': 'Payment Received',
            'overdue': 'Payment Overdue'
        }
        return statuses.get(self.status, self.status)
