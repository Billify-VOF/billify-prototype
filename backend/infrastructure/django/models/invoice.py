"""Django ORM model for invoice persistence and database operations."""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Invoice(models.Model):
    """Database model for storing invoice information."""

    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Payment Received'),
        ('overdue', 'Payment Overdue'),
    ]

    # Core invoice data
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    file_path = models.CharField(max_length=255)

    # Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        """Model configuration for database behavior and indexing."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} ({self.status})"

    def is_overdue(self) -> bool:
        """Check if the invoice is past its due date."""
        return self.due_date < timezone.now().date()

    def mark_as_overdue(self) -> None:
        """Mark the invoice as overdue if past due date."""
        if self.is_overdue() and self.status == 'pending':
            self.status = 'overdue'
            self.save(update_fields=['status', 'updated_at'])
