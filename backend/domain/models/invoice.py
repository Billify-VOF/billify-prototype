"""Domain model representing an invoice and its business rules."""

from decimal import Decimal
from datetime import date
from typing import Optional
from domain.exceptions import InvalidInvoiceError
from .value_objects import UrgencyLevel, InvoiceStatus
from django.utils import timezone


class Invoice:
    """
    Represents an invoice in our system, containing all relevant
    business data and validation rules.

    Attributes:
        id (Optional[int]): Database ID if persisted
        amount (Decimal): Invoice amount (must be positive)
        due_date (date): When payment is due
        invoice_number (str): Unique identifier
        file_path (str): Path to stored PDF file
        status (InvoiceStatus): Current payment status
        _manual_urgency (Optional[UrgencyLevel]): Manual urgency override
    """

    def __init__(
        self,
        amount: Decimal,
        due_date: date,
        invoice_number: str,
        file_path: str,
        invoice_id: Optional[int] = None
    ):
        self.id: Optional[int] = invoice_id
        self.amount: Decimal = amount
        self.due_date: date = due_date
        self.invoice_number: str = invoice_number
        self.file_path: str = file_path
        self.status: InvoiceStatus = InvoiceStatus.PENDING
        self._manual_urgency: Optional[UrgencyLevel] = None

    def validate(self) -> None:
        """Apply business rules to validate invoice data."""
        if self.amount <= 0:
            raise InvalidInvoiceError("Invoice amount must be positive")
        # if self.due_date < date.today():
        # raise InvalidInvoiceError("Due date cannot be in the past")

    def get_status_display(self) -> str:
        """Return a human-readable status description."""
        return self.status.display_name

    def is_overdue(self) -> bool:
        """Check if the invoice is past its due date.
        
        Returns:
            bool: True if the invoice is past its due date, False otherwise.
        """
        return self.due_date < timezone.now().date()

    def mark_as_overdue(self) -> None:
        """Mark the invoice as overdue if it's past due date and pending.
        
        This method will only mark the invoice as overdue if:
        1. The invoice is past its due date
        2. The current status is 'pending'
        
        The status change will be persisted through the repository pattern.
        """
        if self.is_overdue() and self.status == InvoiceStatus.PENDING:
            self.status = InvoiceStatus.OVERDUE
            # Note: Persistence handled by repository

    def validate_status(self) -> None:
        """Validate invoice status against business rules.
        
        Raises:
            InvalidInvoiceError: If status violates business rules
        """
        if self.status == InvoiceStatus.OVERDUE and self.due_date > timezone.now().date():
            raise InvalidInvoiceError('Invoice cannot be overdue if due date is in the future')

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
            InvalidInvoiceError: If new_urgency is not a UrgencyLevel instance
        """
        if not isinstance(new_urgency, UrgencyLevel):
            raise InvalidInvoiceError(f"Expected UrgencyLevel, got {type(new_urgency)}")
        self._manual_urgency = new_urgency

    def clear_manual_urgency(self) -> None:
        """Clear the manual override for the invoice's urgency level.

        After clearing, the urgency will be automatically calculated
        based on the due date.

        Returns:
            None
        """
        self._manual_urgency = None
