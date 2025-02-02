"""Django ORM model for invoice persistence and database operations."""

from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from domain.models.value_objects import InvoiceStatus, UrgencyLevel


class Invoice(models.Model):
    """Database model for storing invoice information.
    
    This model handles the persistence of invoice data extracted from PDF files.
    It focuses on data integrity and storage, while business logic is handled
    in the domain model.

    Key Assumptions:
        - Invoices can only be created from PDF files
        - Maximum invoice amount is 99,999,999.99
        - Invoice numbers are unique but format varies by country
        - Status transitions are managed by the domain model
        - Timestamps are automatically managed by Django
    """

    objects = models.Manager()

    # Core invoice data
    invoice_number = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique identifier for the invoice. "
                  "Can contain special characters and varies by country format."
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total invoice amount. "
                  "Maximum 99,999,999.99. "
                  "Negative amounts not allowed."
    )
    due_date = models.DateField(
        help_text="Date when payment is due. "
                  "Used for overdue calculations and urgency levels."
    )

    # Metadata
    # Status
    STATUS_CHOICES = InvoiceStatus.choices()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current payment status of the invoice. "
                  "Automatically updated based on payment and due date."
    )

    URGENCY_LEVELS = UrgencyLevel.choices()
    manual_urgency = models.IntegerField(
        choices=URGENCY_LEVELS,
        null=True,
        blank=True,
        help_text="Manual override for invoice urgency. "
                  "If not set, urgency is calculated from due date."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # File handling
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text="User who uploaded the invoice PDF. "
                  "Protected from deletion."
    )
    file_path = models.CharField(
        max_length=255,
        help_text="Relative path to the stored invoice PDF file in the system."
    )

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

    def __str__(self) -> str:
        return f"Invoice {self.invoice_number} ({self.status})"

    def __init__(
            self,
            invoice_number: str, 
            amount: Decimal,
            due_date: date,
            uploaded_by_id: int,
            file_path: str,
            *args, 
            **kwargs
    ):
        """Initialize a new Invoice instance.

        Args:
            invoice_number (str): Unique identifier extracted from PDF
            amount (Decimal): Invoice amount extracted from PDF
            due_date (date): Due date extracted from PDF
            uploaded_by_id (int): ID of the user who uploaded the invoice
            file_path (str): Path to the stored PDF file
            *args: Additional positional arguments for Django model
            **kwargs: Additional keyword arguments for Django model

        Note:
            All parameters are required as we only support PDF-based invoice creation.
            Status and urgency are handled automatically and should not be provided.
            Business rule validation happens in the domain model before reaching this class.
        """
        # Initialize Django model
        super().__init__(
            invoice_number = invoice_number,
            amount = amount,
            due_date = due_date,
            uploaded_by_id = uploaded_by_id,
            file_path = file_path,
            *args, 
            **kwargs
        )

    def clean(self) -> None:
        """Validate the model as a whole.
        
        Validates only data integrity constraints. Business rules are handled in the domain model.
        
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
            ValidationError: If manual_urgency is set but not a valid UrgencyLevel db_value
        """
        if self.manual_urgency is not None:
            valid_levels = [level.db_value for level in UrgencyLevel]
            if self.manual_urgency not in valid_levels:
                raise ValidationError({
                    'manual_urgency': f'Invalid urgency level. Must be one of: {valid_levels}'
                })
