"""Domain model representing an invoice and its business rules."""

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional
from domain.exceptions import InvalidInvoiceError
from domain.models.value_objects import UrgencyLevel, InvoiceStatus
from django.utils import timezone
from logging import getLogger

# Module-level logger
logger = getLogger(__name__)


@dataclass
class BuyerInfo:
    name: Optional[str] = None
    address: Optional[str] = None
    vat: Optional[str] = None
    email: Optional[str] = None


@dataclass
class SellerInfo:
    name: Optional[str] = None
    vat: Optional[str] = None


@dataclass
class PaymentInfo:
    method: Optional[str] = None
    currency: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    processor: Optional[str] = None
    transaction_id: Optional[str] = None
    subtotal: Optional[Decimal] = None
    vat_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None


@dataclass
class FileInfo:
    path: Optional[str] = None
    size: Optional[int] = None
    file_type: Optional[str] = None
    original_name: Optional[str] = None


class Invoice:
    """
    Represents an invoice in our system, containing all relevant
    business data and validation rules.

    Attributes:
        id (Optional[int]): Database ID if persisted
        amount (Decimal): Invoice amount (must be positive)
        due_date (date): When payment is due
        invoice_number (str): Unique identifier
        status (InvoiceStatus): Current payment status
        _manual_urgency (Optional[UrgencyLevel]): Manual urgency override
    """

    @classmethod
    def create(
        cls,
        amount: Decimal,
        due_date: date,
        invoice_number: str,
        status: InvoiceStatus = InvoiceStatus.PENDING,
        buyer: Optional[BuyerInfo] = None,
        seller: Optional[SellerInfo] = None,
        payment: Optional[PaymentInfo] = None,
        file: Optional[FileInfo] = None,
        uploaded_by=None,
    ) -> "Invoice":
        """Create a new valid invoice.

        Factory method that creates and validates a new invoice instance.
        Use this method instead of constructor for normal invoice creation.

        Args:
            amount (Decimal): Invoice amount (must be positive)
            due_date (date): When payment is due
            invoice_number (str): Unique identifier
            status (InvoiceStatus, optional): Initial status.
                Defaults to PENDING.

        Returns:
            Invoice: A validated invoice instance

        Raises:
            InvalidInvoiceError: If any of the data is invalid:
                - Amount is not positive
                - Status is not a valid InvoiceStatus
                - Other validation rules
        """
        invoice = cls(
            amount=amount,
            due_date=due_date,
            invoice_number=invoice_number,
            status=status,
            buyer=buyer,
            seller=seller,
            payment=payment,
            file=file,
            uploaded_by=uploaded_by,
        )
        invoice.validate()
        return invoice

    # class Invoice:
    def __init__(
        self,
        *,
        amount: Decimal,
        due_date: date,
        invoice_number: str,
        uploaded_by: Optional[int] = None,
        status: InvoiceStatus = InvoiceStatus.PENDING,
        invoice_id: Optional[int] = None,
        buyer: Optional[BuyerInfo] = None,
        seller: Optional[SellerInfo] = None,
        payment: Optional[PaymentInfo] = None,
        file: Optional[FileInfo] = None,
    ) -> None:
        logger.debug("Invoice __init__ called")
        logger.debug("  amount: %s (%s)", amount, type(amount))
        logger.debug("  due_date: %s (%s)", due_date, type(due_date))
        logger.debug("  invoice_number: %s (%s)", invoice_number, type(invoice_number))

        self.id: Optional[int] = invoice_id
        self.amount: Decimal = amount
        self.due_date: date = due_date
        self.invoice_number: str = invoice_number
        self.status: InvoiceStatus = status
        self.uploaded_by: Optional[int] = uploaded_by

        self.buyer = buyer or BuyerInfo()  # Avoid None checks later
        self.seller = seller or SellerInfo()
        self.payment = payment or PaymentInfo()
        self.file = file or FileInfo()
        self._manual_urgency: Optional[UrgencyLevel] = None

    def validate(self) -> None:
        """Apply business rules to validate invoice data."""
        if self.amount <= 0:
            raise InvalidInvoiceError("Invoice amount must be positive")
        self.validate_status()

    def validate_status(self) -> None:
        """Validate invoice status against business rules.

        Raises:
            InvalidInvoiceError: If status violates business rules
        """
        if self.status == InvoiceStatus.OVERDUE and self.due_date > timezone.now().date():
            raise InvalidInvoiceError("Invoice cannot be overdue if due date is in the future")
        if not isinstance(self.status, InvoiceStatus):
            raise InvalidInvoiceError("Status must be an InvoiceStatus enum")
        valid_statuses = (InvoiceStatus.PENDING, InvoiceStatus.OVERDUE, InvoiceStatus.PAID)
        if self.status not in valid_statuses:
            raise InvalidInvoiceError(f"Invalid status: {self.status}")

    @property
    def is_paid(self) -> bool:
        """Check if the invoice has been paid.

        Returns:
            bool: True if the invoice status is PAID, False otherwise.

        Example:
            invoice = Invoice(...)
            invoice.mark_as_paid()
            invoice.is_paid  # Returns True

            invoice = Invoice(...)  # New invoice
            invoice.is_paid  # Returns False (PENDING by default)
        """
        return self.status == InvoiceStatus.PAID

    @property
    def urgency(self) -> "UrgencyLevel":
        """Returns current urgency level: manual override or calculated.

        The urgency level can be either:
        1. A manually set override (if _manual_urgency is not None)
        2. Automatically calculated based on days until due date

        Calculation Rules:
        - OVERDUE:  Past due date (days < 0)
        - CRITICAL: Due within 7 days (0-7 days)
        - HIGH:     Due in 8-14 days
        - MEDIUM:   Due in 15-30 days
        - LOW:      Due in 31+ days

        Technical Details:
        - Uses UrgencyLevel.calculate_from_days() for automatic calculation
        - Calculates days as (due_date - today).days
        - Returns _manual_urgency directly if set

        Returns:
            UrgencyLevel: The current urgency level enum instance

        Example:
            invoice = Invoice(due_date=date.today() + timedelta(days=5))
            invoice.urgency  # Returns UrgencyLevel.CRITICAL

            invoice.set_urgency_manually(UrgencyLevel.HIGH)
            invoice.urgency  # Returns UrgencyLevel.HIGH (manual override)
        """
        if self._manual_urgency is not None:
            return self._manual_urgency
        today = date.today()
        due_date_timedelta = self.due_date - today
        days_until_due = due_date_timedelta.days
        return UrgencyLevel.calculate_from_days(days_until_due)

    def is_urgency_manually_set(self) -> bool:
        """Check if the urgency level has been manually set.

        Returns:
            bool: True if urgency has been manually overridden, False if it's calculated automatically
        """
        return self._manual_urgency is not None

    def get_status_display(self) -> str:
        """Return a human-readable status description."""
        return self.status.display_name

    def mark_as_paid(self) -> None:
        """Mark the invoice as paid.

        This method will only mark the invoice as paid if:
        1. The current status is 'pending' or 'overdue'
        2. The invoice hasn't been paid yet

        Raises:
            InvalidInvoiceError: If invoice is already paid

        The status change will be persisted through the repository pattern.
        """
        if self.status == InvoiceStatus.PENDING or self.status == InvoiceStatus.OVERDUE:
            self.status = InvoiceStatus.PAID

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

    def set_urgency_manually(self, new_urgency: UrgencyLevel) -> None:
        """Set a manual override for the invoice's urgency level.

        This method allows overriding the automatically calculated urgency
        with a manually specified level. The override remains in effect until
        clear_manual_urgency() is called.

        Args:
            new_urgency (UrgencyLevel): The urgency level to set manually.
                Must be a valid UrgencyLevel enum instance.

        Raises:
            InvalidInvoiceError: If new_urgency is not a UrgencyLevel instance

        Example:
            invoice = Invoice(...)
            # Set manual urgency
            invoice.set_urgency_manually(UrgencyLevel.HIGH)
            invoice.urgency  # Returns UrgencyLevel.HIGH regardless of due date

            # Trying to set invalid urgency
            invoice.set_urgency_manually("HIGH")  # Raises InvalidInvoiceError
        """
        if not isinstance(new_urgency, UrgencyLevel):
            raise InvalidInvoiceError(f"Expected UrgencyLevel, got {type(new_urgency)}")
        self._manual_urgency = new_urgency
        logger.debug("Update: Setting manual urgency to %s", new_urgency)

    def clear_manual_urgency(self) -> None:
        """Clear the manual override for the invoice's urgency level.

        After clearing, the urgency will be automatically calculated
        based on the due date using UrgencyLevel.calculate_from_days().

        This method:
        1. Sets _manual_urgency to None
        2. Allows automatic urgency calculation to resume
        3. Takes effect immediately (next urgency property access)

        Example:
            invoice = Invoice(due_date=date.today() + timedelta(days=5))
            invoice.urgency  # Returns UrgencyLevel.CRITICAL (automatic)

            invoice.set_urgency_manually(UrgencyLevel.LOW)
            invoice.urgency  # Returns UrgencyLevel.LOW (manual override)

            invoice.clear_manual_urgency()
            invoice.urgency  # Returns UrgencyLevel.CRITICAL (automatic again)
        """
        self._manual_urgency = None
        logger.debug("Update: Clearing manual urgency override")

    def update(self, **kwargs) -> None:
        """Update invoice fields with validation.

        Updates fields while ensuring validation rules are met.

        Args:
            **kwargs: Field updates as keyword arguments, which can include:
                amount (Decimal): New invoice amount
                due_date (date): New due date
                invoice_number (str): New invoice number
                status (InvoiceStatus): New invoice status
                manual_urgency (UrgencyLevel or False): New urgency level
                    or False to clear manual urgency
                buyer_name, buyer_address, buyer_vat, buyer_email: Buyer fields
                seller_name, seller_vat: Seller fields
                payment_method, currency, iban, bic: Payment fields
                payment_processor, transaction_id: Payment processor fields
                subtotal, vat_amount, total_amount: Amount fields
                file_size, file_type, original_file_name: File metadata
        """
        # Use only non-None values
        fields_to_update = {k: v for k, v in kwargs.items() if v is not None}

        # Handle manual urgency separately
        if "manual_urgency" in fields_to_update:
            urgency_value = fields_to_update.pop("manual_urgency")
            if urgency_value is False:
                self.clear_manual_urgency()
            elif isinstance(urgency_value, UrgencyLevel):
                self.set_urgency_manually(urgency_value)
            else:
                raise InvalidInvoiceError(f"Expected UrgencyLevel or False, got {type(urgency_value)}")

        # Apply updates dynamically
        for field, value in fields_to_update.items():
            setattr(self, field, value)

        # Validate the updated invoice
        self.validate()
