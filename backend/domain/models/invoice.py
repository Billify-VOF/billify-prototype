"""Domain model representing an invoice and its business rules."""

from decimal import Decimal
from datetime import date
from typing import Optional
from domain.exceptions import InvalidInvoiceError
from .value_objects import UrgencyLevel


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
        self._manual_urgency = None  # Default: no override

    def validate(self):
        """Apply business rules to validate invoice data."""
        if self.amount <= 0:
            raise InvalidInvoiceError("Invoice amount must be positive")
        # if self.due_date < date.today():
        # raise InvalidInvoiceError("Due date cannot be in the past")

    def get_status_display(self) -> str:
        """Return a human-readable status description."""
        statuses = {
            'pending': 'Pending Payment',
            'paid': 'Payment Received',
            'overdue': 'Payment Overdue'
        }
        return statuses.get(self.status, self.status)

    @property
    def urgency(self) -> 'UrgencyLevel':
        """
        Returns the Urgency Level of an Invoice instance based on the due date.

        Urgency levels are calculated based on days until due:
        - OVERDUE: Past due date (Dark Red)
        - CRITICAL: Due within 7 days (Red)
        - HIGH: Due in 8-14 days (Orange)
        - MEDIUM: Due in 15-30 days (Yellow)
        - LOW: Due in 31+ days (Green)

        Returns:
            UrgencyLevel: The calculated urgency level based on days until
            due date.
        """
        if self._manual_urgency is not None:
            return self._manual_urgency
        today = date.today()
        due_date_timedelta = self.due_date - today
        days_until_due = due_date_timedelta.days
        return UrgencyLevel.calculate_from_days(days_until_due)

    def set_urgency_manually(self, new_urgency: UrgencyLevel) -> None:
        """
        Set a manual override for the invoice's urgency level.

        Args:
            new_urgency (UrgencyLevel): The urgency level to set manually

        Raises:
            ValueError: If new_urgency is not a UrgencyLevel instance
        """
        # Runtime type check for defensive programming.
        # While the type hint suggests this is unreachable,
        # we keep it to guard against runtime type violations.
        if not isinstance(new_urgency, UrgencyLevel):
            raise ValueError(f"Expected UrgencyLevel, got {type(new_urgency)}")
        self._manual_urgency = new_urgency

    def clear_manual_urgency(self) -> None:
        """Clear the manual override for the invoice's urgency level.

        After clearing, the urgency will be automatically calculated
        based on the due date.

        Returns:
            None
        """
        self._manual_urgency = None
