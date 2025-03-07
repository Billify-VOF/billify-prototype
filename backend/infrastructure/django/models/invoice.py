"""Django ORM model for invoice persistence and database operations."""

from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from domain.models.value_objects import InvoiceStatus, UrgencyLevel
from logging import getLogger
from typing import Optional

# Module-level logger
logger = getLogger(__name__)


class Invoice(models.Model):
    """Database model for storing invoice information.

    This model handles the persistence of invoice data extracted from PDF
    files. It focuses on data integrity and storage, while business logic
    is handled in the domain model.

    Attributes:
        id (AutoField): Primary key, automatically added by Django.
                     Auto-incrementing integer field that uniquely
                     identifies each invoice.
        invoice_number (CharField): Business-specific unique identifier
        amount (DecimalField): Total invoice amount
        due_date (DateField): When payment is due
        status (CharField): Current payment status
        uploaded_by (ForeignKey): User who uploaded the invoice
        created_at (DateTimeField): When the record was created
        updated_at (DateTimeField): When the record was last modified

    Key Assumptions:
        - Invoices can only be created from PDF files
        - Maximum invoice amount is 99,999,999.99
        - Invoice numbers are unique but format varies by country
        - Status transitions are managed by the domain model
        - Timestamps are automatically managed by Django
    """

    objects = models.Manager()

    # Core invoice data
    invoice_number: models.CharField = models.CharField(
        max_length=100,
        help_text=(
            "Business-specific identifier for the invoice. "
            "Can contain special characters and varies by country format. "
            "Note: Invoice numbers may be similar or identical due to: "
            "1) Different suppliers using the same numbering format "
            "2) OCR extraction errors requiring manual correction "
            "3) Initial automated extraction before user verification "
            "4) Manual edits during the invoice review process. "
            "Therefore, invoice numbers are not constrained to be unique."
        )
    )
    amount: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total invoice amount. "
                  "Maximum 99,999,999.99. "
                  "Negative amounts not allowed."
    )
    due_date: models.DateField = models.DateField(
        help_text="Date when payment is due. "
                  "Used for overdue calculations and urgency levels."
    )

    # Metadata
    # Status
    STATUS_CHOICES = InvoiceStatus.choices()
    status: models.CharField = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current payment status of the invoice. "
                  "Automatically updated based on payment and due date."
    )

    URGENCY_LEVELS = UrgencyLevel.choices()
    manual_urgency: models.IntegerField = models.IntegerField(
        choices=URGENCY_LEVELS,
        null=True,
        blank=True,
        help_text="Manual override for invoice urgency. "
                  "If not set, urgency is calculated from due date."
    )

    # Timestamps
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    # File handling
    uploaded_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text="User who uploaded the invoice PDF. "
                  "Protected from deletion."
    )
    uploaded_by_id: int

    file_path: models.CharField = models.CharField(
        max_length=255,
        help_text="Relative path to the stored invoice PDF file in the system."
    )

    # Meta Data
    buyer_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_address = models.TextField(null=True, blank=True)
    buyer_email = models.EmailField(null=True, blank=True)
    buyer_vat = models.CharField(max_length=50, null=True, blank=True)
    seller_name = models.CharField(max_length=255, null=True, blank=True)
    seller_vat = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    iban = models.CharField(max_length=34, null=True, blank=True)
    bic = models.CharField(max_length=11, null=True, blank=True)
    payment_processor = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)

    file_size = models.BigIntegerField(null=True, blank=True, help_text="Size of the uploaded file in bytes.")
    file_type = models.CharField(max_length=100, null=True, blank=True, help_text="MIME type of the uploaded file.")
    original_file_name = models.CharField(max_length=255, null=True, blank=True, help_text="Original name of the uploaded file.")


    class Meta:
        """Model configuration for database behavior and indexing.

        Indexes are created for:
            - invoice_number: For unique constraint lookups
            - status: For filtering and status-based queries
            - due_date: For overdue calculations and date-based filtering
        """
        app_label = 'infrastructure'
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    @classmethod
    def create(
        cls,
    invoice_number: str,
    amount: Decimal,
    due_date: date,
    uploaded_by: int,  # Change from uploaded_by_id
    file_path: str,
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
    original_file_name: Optional[str] = None 

    ) -> 'Invoice':
        """Create a new Invoice instance with validation."""
        instance = cls(
            invoice_number=invoice_number,
        amount=amount,
        due_date=due_date,
        uploaded_by_id=uploaded_by,
        file_path=file_path,
        buyer_name=buyer_name or "",
        buyer_address=buyer_address or "",
        buyer_vat=buyer_vat or "",
        buyer_email=buyer_email or "",
        seller_name=seller_name or "",
        seller_vat=seller_vat or "",
        payment_method=payment_method or "",
        currency=currency or "",
        iban=iban or "",
        bic=bic or "",
        payment_processor=payment_processor or "",
        transaction_id=transaction_id or "",
        subtotal=subtotal or Decimal("0.00"),
        vat_amount=vat_amount or Decimal("0.00"),
        total_amount=total_amount or Decimal("0.00"),
        file_size=file_size or 0,
        file_type=file_type or "unknown",
        original_file_name=original_file_name or "unknown"
        )
        instance.full_clean()
        return instance

    def __str__(self) -> str:
        return f"Invoice {self.invoice_number} ({self.status})"

    def __init__(self, *args, **kwargs):
        """Initialize a new Invoice instance.

        Note:
            This simplified constructor allows Django's ORM to work correctly
            while the create() class method provides a validated way to
            create new instances.
        """
        logger.debug("Django Invoice __init__ called")
        logger.debug("Number of args: %s", len(args))
        for i, arg in enumerate(args):
            logger.debug("arg[%s]: %s (type: %s)", i, arg, type(arg))
        logger.debug("kwargs: %s", kwargs)
        super().__init__(*args, **kwargs)

    def clean(self) -> None:
        """Validate the model as a whole.

        Validates only data integrity constraints. Business rules are
        handled in the domain model.

        Raises:
            ValidationError: If any validation fails
        """
        # Run base parent model validations before custom validations
        super().clean()
        self._validate_urgency_level()

    def _validate_urgency_level(self) -> None:
        """Validate urgency level constraints.

        Validates that if a manual urgency override is set, it uses a valid
        urgency level value from the UrgencyLevel enum.

        Raises:
            ValidationError: If manual_urgency is not a valid UrgencyLevel
                           db_value
        """
        if self.manual_urgency is not None:
            valid_levels = [level.db_value for level in UrgencyLevel]
            if self.manual_urgency not in valid_levels:
                raise ValidationError({
                    'manual_urgency': (
                        'Invalid urgency level. '
                        f'Must be one of: {valid_levels}'
                    )
                })

    def update(
        self,
        *,
        amount: Optional[Decimal] = None,
        due_date: Optional[date] = None,
        status: Optional[str] = None,
        manual_urgency: Optional[int] = None,
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
        uploaded_by: Optional[int] = None,
        file_size: Optional[int] = None,
        file_type: Optional[str] = None,
        original_file_name: Optional[str] = None

    ) -> None:
        """Update invoice fields with validation.

        Encapsulates updates to invoice fields, ensuring proper validation
        is performed before saving changes.

        Args:
            amount: New invoice amount
            due_date: New invoice due date
            status: New invoice status
            uploaded_by_id: ID of user performing the update
            manual_urgency: Manual override for invoice urgency level

        Raises:
            ValidationError: If updated fields don't meet validation
                requirements
        """
        if amount is not None:
            self.amount = amount

        if due_date is not None:
            self.due_date = due_date

        if status is not None:
            self.status = status

        if manual_urgency is not None:
            self.manual_urgency = manual_urgency

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

        if uploaded_by is not None:
            self.uploaded_by = uploaded_by


        if file_size is not None:
            self.file_size = file_size


        if file_type is not None:
            self.file_type = file_type


        if original_file_name is not None:
            self.original_file_name = original_file_name


        # Validate all fields
        self.full_clean()
