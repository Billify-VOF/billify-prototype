"""Serializers for invoice-related API endpoints."""

from rest_framework import serializers


class InvoiceUploadSerializer(serializers.Serializer):
    """
    Validate invoice uploads according to business rules.

    This serializer is used solely for validating uploaded invoice files
    and doesn't handle database operations directly. Instead, it passes
    validated data to the InvoiceService for business logic processing.
    """

    file = serializers.FileField()

    def validate_file(self, value):
        """
        Ensure uploaded invoice meets business requirements:
        - Must be PDF format
        - Must not exceed maximum allowed size
        - Must have valid filename
        """
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError(
                "Invalid invoice format. Please upload PDF files only."
            )

        # Size limit from business requirements
        max_size = 10 * 1024 * 1024  # 10 MB
        if value.size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise serializers.ValidationError(
                f"Invoice file exceeds maximum allowed size of {max_mb}MB."
            )

        return value

    def create(self, *_):
        """Not used - this serializer only validates file uploads."""
        raise NotImplementedError(
            "InvoiceUploadSerializer is for validation only. "
            "Use InvoiceService for invoice creation."
        )

    def update(self, *_):
        """
        Not used - this serializer only validates file uploads.

        Our architecture delegates invoice updates to the InvoiceService
        in the domain layer rather than handling it in the serializer.

        Raises:
            NotImplementedError: This serializer doesn't update objects
        """
        raise NotImplementedError(
            "InvoiceUploadSerializer is for validation only. "
            "Use InvoiceService for invoice updates."
        )
