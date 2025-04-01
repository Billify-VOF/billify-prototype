"""Django ORM model for invoice persistence and database operations."""

from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from domain.models.value_objects import InvoiceStatus, UrgencyLevel
from logging import getLogger
from typing import Any

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
        ),
    )
    amount: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total invoice amount. Maximum 99,999,999.99. Negative amounts not allowed.",
    )
    due_date: models.DateField = models.DateField(
        help_text="Date when payment is due. Used for overdue calculations and urgency levels."
    )

    # Metadata
    # Status
    STATUS_CHOICES = InvoiceStatus.choices()
    status: models.CharField = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current payment status of the invoice. "
        "Automatically updated based on payment and due date.",
    )

    URGENCY_LEVELS = UrgencyLevel.choices()
    manual_urgency: models.IntegerField = models.IntegerField(
        choices=URGENCY_LEVELS,
        null=True,
        blank=True,
        help_text="Manual override for invoice urgency. If not set, urgency is calculated from due date.",
    )

    # Timestamps
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    # File handling
    uploaded_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text="User who uploaded the invoice PDF. Protected from deletion.",
    )
    uploaded_by_id: int

    file_path: models.CharField = models.CharField(
        max_length=255, help_text="Relative path to the stored invoice PDF file in the system."
    )

    # Meta Data
    buyer_name: models.CharField = models.CharField(max_length=255, null=True, blank=True)
    buyer_address: models.TextField = models.TextField(null=True, blank=True)
    buyer_email: models.EmailField = models.EmailField(null=True, blank=True)
    buyer_vat: models.CharField = models.CharField(max_length=50, null=True, blank=True)
    seller_name: models.CharField = models.CharField(max_length=255, null=True, blank=True)
    seller_vat: models.CharField = models.CharField(max_length=50, null=True, blank=True)
    payment_method: models.CharField = models.CharField(max_length=50, null=True, blank=True)
    currency: models.CharField = models.CharField(max_length=10, null=True, blank=True)
    iban: models.CharField = models.CharField(max_length=34, null=True, blank=True)
    bic: models.CharField = models.CharField(max_length=11, null=True, blank=True)
    payment_processor: models.CharField = models.CharField(max_length=100, null=True, blank=True)
    transaction_id: models.CharField = models.CharField(max_length=100, null=True, blank=True)
    subtotal: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    vat_amount: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total_amount: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    invoice_date: models.DateField = models.DateField(null=True, blank=True)

    file_size: models.BigIntegerField = models.BigIntegerField(
        null=True, blank=True, help_text="Size of the uploaded file in bytes."
    )
    file_type: models.CharField = models.CharField(
        max_length=100, null=True, blank=True, help_text="MIME type of the uploaded file."
    )
    original_file_name: models.CharField = models.CharField(
        max_length=255, null=True, blank=True, help_text="Original name of the uploaded file."
    )

    class Meta:
        """Model configuration for database behavior and indexing.

        Indexes are created for:
            - invoice_number: For unique constraint lookups
            - status: For filtering and status-based queries
            - due_date: For overdue calculations and date-based filtering
        """

        app_label = "infrastructure"
        ordering = ["-created_at"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    @classmethod
    def create(
        cls,
        invoice_number: str,
        amount: Decimal,
        due_date: date,
        uploaded_by: int,
        file_path: str,
        **optional_fields: Any,
    ) -> "Invoice":
        """Create a new Invoice instance with validation.

        Args:
            invoice_number: Business identifier of the invoice
            amount: Total invoice amount
            due_date: When payment is due
            uploaded_by: User ID who uploaded the invoice
            file_path: Path to the stored invoice file
            **optional_fields: Additional fields like buyer_name, seller_name, etc.
        """
        instance = cls(
            invoice_number=invoice_number,
            amount=amount,
            due_date=due_date,
            uploaded_by_id=uploaded_by,
            file_path=file_path,
            **optional_fields,
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
        if self.amount is not None and self.amount < 0:
            raise ValidationError({"amount": "Negative amounts are not allowed."})
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
                raise ValidationError(
                    {"manual_urgency": f"Invalid urgency level. Must be one of: {valid_levels}"}
                )

    def update(self, **fields_to_update: Any) -> None:
        """Update invoice fields with validation.

        Updates only the fields that are provided in kwargs, ensuring proper validation.

        Args:
            **fields_to_update: Fields to update (amount, due_date, status, etc.)

        Raises:
            ValidationError: If updated fields don't meet validation requirements.
        """
        # Handle UrgencyLevel conversion if present
        if "manual_urgency" in fields_to_update and isinstance(
            fields_to_update["manual_urgency"], UrgencyLevel
        ):
            fields_to_update["manual_urgency"] = fields_to_update["manual_urgency"].db_value

        # Update fields
        for field, value in fields_to_update.items():
            setattr(self, field, value)

        # Validate all fields
        self.full_clean()
