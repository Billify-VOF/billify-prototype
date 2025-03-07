"""Domain model representing an invoice and its business rules."""

from decimal import Decimal
from datetime import date
from typing import Optional, Union
from domain.exceptions import InvalidInvoiceError
from domain.models.value_objects import UrgencyLevel, InvoiceStatus
from django.utils import timezone
from logging import getLogger

# Module-level logger
logger = getLogger(__name__)


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
    def create(cls,
                amount: Decimal,
                due_date: date,
                invoice_number: str,
                status: InvoiceStatus = InvoiceStatus.PENDING,
                file_size: Optional[int] = None,  
                file_type: Optional[str] = None, 
                file_path=None,
                uploaded_by=None,
                original_file_name: Optional[str] = None, 
                buyer_name: Optional[str] = None,
                buyer_address: Optional[str] = None,
                buyer_vat: Optional[str] = None,
                buyer_email: Optional[str] = None,
                seller_name: Optional[str] = None,        
                seller_vat: Optional[str] = None,        
                payment_method: Optional[str] = None,        
                currency: Optional[str] = None,        
                iban: Optional[str] = None,        
                bic: Optional[str] = None,        
                payment_processor: Optional[str] = None,        
                transaction_id: Optional[str] = None, 
                subtotal: Optional[Decimal] = None,       
                vat_amount: Optional[Decimal] = None,       
                total_amount: Optional[Decimal] = None,
               ) -> 'Invoice':
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
            file_size=file_size,
            file_path=file_path,
            file_type=file_type,
            original_file_name=original_file_name,
            status=status,
            uploaded_by=uploaded_by
        )
        invoice.validate()
        return invoice

    def __init__(
        self,
        *,  # This makes all following arguments keyword-only
        amount: Decimal,
        due_date: date,
        invoice_number: str,
        uploaded_by: None,
        file_path:  Optional[str] = None,
        invoice_id: Optional[int] = None,
        status: InvoiceStatus = InvoiceStatus.PENDING,
        buyer_name: Optional[str] = None,
        buyer_address: Optional[str] = None,
        buyer_vat: Optional[str] = None,
        buyer_email: Optional[str] = None,
        seller_name: Optional[str] = None,        
        seller_vat: Optional[str] = None,        
        payment_method: Optional[str] = None,        
        currency: Optional[str] = None,        
        iban: Optional[str] = None,        
        bic: Optional[str] = None,        
        payment_processor: Optional[str] = None,        
        transaction_id: Optional[str] = None, 
        subtotal: Optional[Decimal] = None,       
        vat_amount: Optional[Decimal] = None,       
        total_amount: Optional[Decimal] = None,
        file_size: Optional[int] = None,  # File size in bytes
        file_type: Optional[str] = None,  # MIME type (e.g., "application/pdf")
        original_file_name: Optional[str] = None,  # Original file name

    ) -> None:
        logger.debug("Invoice __init__ called")
        logger.debug("  amount: %s (%s)", amount, type(amount))
        logger.debug("  due_date: %s (%s)", due_date, type(due_date))
        logger.debug(
            "  invoice_number: %s (%s)",
            invoice_number,
            type(invoice_number)
        )
        self.id: Optional[int] = invoice_id
        self.amount: Decimal = amount
        self.due_date: date = due_date
        self.file_path = file_path 
        self.invoice_number: str = invoice_number
        self.status: InvoiceStatus = status
        self._manual_urgency: Optional[UrgencyLevel] = None
        self.buyer_name: Optional[str] = buyer_name
        self.buyer_address: Optional[str] = buyer_address
        self.buyer_vat: Optional[str] = buyer_vat
        self.buyer_email: Optional[str] = buyer_email
        self.seller_name: Optional[str] = seller_name
        self.seller_vat: Optional[str] = seller_vat
        self.payment_method: Optional[str] = payment_method
        self.currency: Optional[str] = currency
        self.iban: Optional[str] = iban
        self.bic: Optional[str] = bic
        self.payment_processor: Optional[str] = payment_processor
        self.transaction_id: Optional[str] = transaction_id
        self.subtotal: Optional[Decimal] = subtotal
        self.vat_amount: Optional[Decimal] = vat_amount
        self.total_amount: Optional[Decimal] = total_amount
        self.uploaded_by:Optional[int] =None

        self.file_size = file_size
        self.file_type = file_type
        self.original_file_name = original_file_name


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
        if (self.status == InvoiceStatus.OVERDUE
                and self.due_date > timezone.now().date()):
            raise InvalidInvoiceError(
                'Invoice cannot be overdue if due date is in the future'
            )
        if not isinstance(self.status, InvoiceStatus):
            raise InvalidInvoiceError("Status must be an InvoiceStatus enum")
        valid_statuses = (
            InvoiceStatus.PENDING,
            InvoiceStatus.OVERDUE,
            InvoiceStatus.PAID
        )
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
    def urgency(self) -> 'UrgencyLevel':
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
        if (self.status == InvoiceStatus.PENDING
                or self.status == InvoiceStatus.OVERDUE):
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
            raise InvalidInvoiceError(
                f"Expected UrgencyLevel, got {type(new_urgency)}"
            )
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

    def update(
        self,
        *,
        amount: Optional[Decimal] = None,
        due_date: Optional[date] = None,
        invoice_number: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
        manual_urgency: Optional[Union[UrgencyLevel, bool]] = None,
        buyer_name: Optional[str] = None,
        buyer_address: Optional[str] = None,
        buyer_vat: Optional[str] = None,
        buyer_email: Optional[str] = None,
        seller_name: Optional[str] = None,        
        seller_vat: Optional[str] = None,        
        payment_method: Optional[str] = None,        
        currency: Optional[str] = None,        
        iban: Optional[str] = None,        
        bic: Optional[str] = None,        
        payment_processor: Optional[str] = None,        
        transaction_id: Optional[str] = None, 
        subtotal: Optional[Decimal] = None,       
        vat_amount: Optional[Decimal] = None,       
        total_amount: Optional[Decimal] = None,
        file_size: Optional[int] = None,
        file_type: Optional[str] = None,
        original_file_name: Optional[str] = None,

    ) -> None:
        """Update invoice fields with validation.

        This method allows updating one or more invoice fields and ensures
        that all business rules are validated after the update.

        Args:
            amount (Optional[Decimal]): New invoice amount
            due_date (Optional[date]): New due date
            invoice_number (Optional[str]): New invoice number
            status (Optional[InvoiceStatus]): New invoice status
            manual_urgency (Optional[Union[UrgencyLevel, bool]]): New urgency level
                or False to clear manual urgency and switch to automatic calculation

        Raises:
            InvalidInvoiceError: If the updated data violates business rules

        Example:
            invoice = Invoice(amount=100, due_date=date(2023, 1, 1),
                             invoice_number="INV-001")

            # Update just the amount
            invoice.update(amount=Decimal("150.00"))

            # Update multiple fields
            invoice.update(
                amount=Decimal("200.00"),
                due_date=date(2023, 2, 1),
                status=InvoiceStatus.PAID
            )
            
            # Set manual urgency alongside other updates
            invoice.update(
                amount=Decimal("300.00"),
                manual_urgency=UrgencyLevel.HIGH
            )
            
            # Clear manual urgency and return to automatic calculation
            invoice.update(manual_urgency=False)
        """
        # Update fields that are provided (not None)
        if amount is not None:
            self.amount = amount

        if due_date is not None:
            self.due_date = due_date

        if invoice_number is not None:
            self.invoice_number = invoice_number

        if status is not None:
            self.status = status

        if buyer_name is not None:
            self.buyer_name = buyer_name

        if buyer_address is not None:
            self.buyer_address = buyer_address

        if buyer_vat is not None:
            self.buyer_vat = buyer_vat


        if buyer_email is not None:
            self.buyer_email = buyer_email


        if seller_name is not None:
            self.seller_name = seller_name


        if seller_vat is not None:
            self.seller_vat = seller_vat


        if payment_method is not None:
            self.payment_method = payment_method


        if currency is not None:
            self.currency = currency


        if iban is not None:
            self.iban = iban


        if bic is not None:
            self.bic = bic


        if payment_processor is not None:
            self.payment_processor = payment_processor


        if transaction_id is not None:
            self.transaction_id = transaction_id


        if subtotal is not None:
            self.subtotal = subtotal


        if vat_amount is not None:
            self.vat_amount = vat_amount


        if total_amount is not None:
            self.total_amount = total_amount

        if file_size is not None:
            self.file_size = file_size

        if file_type is not None:
            self.file_type = file_type

        if original_file_name is not None:
            self.original_file_name = original_file_name
            
        # Handle manual urgency if provided
        if manual_urgency is not None:
            if manual_urgency is False:
                # Special case: False means clear the manual override
                self.clear_manual_urgency()
            elif isinstance(manual_urgency, UrgencyLevel):
                # Set the manual urgency level
                self.set_urgency_manually(manual_urgency)
            else:
                raise InvalidInvoiceError(
                    f"Expected UrgencyLevel or False, got {type(manual_urgency)}"
                )
        else:  # manual_urgency is None
            logger.debug("Update: No change to urgency settings")

        # Validate the updated invoice
        self.validate()
