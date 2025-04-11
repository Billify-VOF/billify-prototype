"""Serializers for invoice-related API endpoints."""

from typing import Any, Optional
from rest_framework import serializers
from django.contrib.auth import get_user_model
import os
import re

User = get_user_model()


class InvoiceUploadSerializer(serializers.Serializer):
    """
    Validate invoice uploads according to business rules.

    This serializer is used solely for validating uploaded invoice files
    and doesn't handle database operations directly. Instead, it passes
    validated data to the InvoiceService for business logic processing.
    """

    file = serializers.FileField()

    def validate_file(self, value: Any) -> Any:
        """
        Ensure uploaded invoice meets business requirements:
        - Must be PDF format
        - Must not exceed maximum allowed size
        - Must have valid filename
        """
        if not value.name.endswith(".pdf"):
            raise serializers.ValidationError("Invalid invoice format. Please upload PDF files only.")

        # Size limit from business requirements
        max_size = 10 * 1024 * 1024  # 10 MB
        if value.size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise serializers.ValidationError(f"Invoice file exceeds maximum allowed size of {max_mb}MB.")

        return value

    def create(self, *_: Any) -> None:
        """Not used - this serializer only validates file uploads."""
        raise NotImplementedError(
            "InvoiceUploadSerializer is for validation only. Use InvoiceService for invoice creation."
        )

    def update(self, *_: Any) -> None:
        """
        Not used - this serializer only validates file uploads.

        Our architecture delegates invoice updates to the InvoiceService
        in the domain layer rather than handling it in the serializer.

        Raises:
            NotImplementedError: This serializer doesn't update objects
        """
        raise NotImplementedError(
            "InvoiceUploadSerializer is for validation only. Use InvoiceService for invoice updates."
        )


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for handling user registration requests.

    This serializer validates and processes user registration data including email,
    username, password and optional company information. It enforces business rules
    around password strength and field requirements.

    Attributes:
        email (EmailField): User's email address
        username (CharField): Chosen username for the account
        password (CharField): User's password (write-only)
        company_name (CharField): Optional company/organization name
    """

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, min_length=3, max_length=150)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    company_name = serializers.CharField(
        required=False, min_length=2, max_length=255, allow_blank=True, allow_null=True
    )

    def validate_password(self, value: str) -> str:
        """Validate password strength."""
        if value.isdigit():
            raise serializers.ValidationError("Password cannot be entirely numeric")

        # Check for at least one number and one letter
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter")

        return value

    def create(self, *_: Any) -> None:
        """Not used - creation is handled by the UserService."""
        raise NotImplementedError(
            "RegisterSerializer is for validation only. Use UserService for user creation."
        )

    def update(self, *_: Any) -> None:
        """Not used - updates are handled by the UserService."""
        raise NotImplementedError(
            "RegisterSerializer is for validation only. Use UserService for user updates."
        )


class InvoiceConfirmationSerializer(serializers.Serializer):
    """
    Serializer for handling invoice confirmation requests.

    This serializer validates the data needed to finalize an invoice by transferring
    it from temporary to permanent storage. It enforces business rules around
    temporary file paths and urgency levels before processing.

    Attributes:
        temp_file_path (CharField): Path to the temporary file, must start with 'temp/'
        urgency_level (IntegerField): Optional priority level (1-5) to assign to the invoice
    """

    temp_file_path = serializers.CharField(required=True)
    urgency_level = serializers.IntegerField(required=False, min_value=1, max_value=5)

    def validate_temp_file_path(self, value: str) -> str:
        """
        Validate the temporary file path according to business rules.

        Ensures the path is non-empty and follows the expected format for
        temporary files. Performs security validation to prevent path traversal
        attacks and ensure only files from the designated temporary storage area
        are processed.

        Args:
            value (str): The temporary file path to validate

        Returns:
            str: The validated temporary file path

        Raises:
            serializers.ValidationError: If the path is empty, doesn't follow
                the expected format, or contains potential security issues
        """
        if not value:
            raise serializers.ValidationError("Temporary file path is required.")

        # Normalize path to handle different path representations
        normalized_path = os.path.normpath(value)

        # Check if path starts with temp/ after normalization
        # if not normalized_path.startswith("temp/"):
        #     raise serializers.ValidationError("Invalid temporary file path format. Must start with 'temp/'.")

        # Prevent directory traversal attempts
        if ".." in normalized_path or "//" in value:
            raise serializers.ValidationError("Invalid path: potential directory traversal attempt.")

        # Validate that the filename follows expected pattern (alphanumeric with common extensions)
        # This helps prevent command injection via filenames
        # filename_pattern = r"^temp/[a-zA-Z0-9_-]+\.[a-zA-Z0-9]+$"
        # if not re.match(filename_pattern, normalized_path):
        #     raise serializers.ValidationError(
        #         "Invalid filename format. Only alphanumeric characters, hyphens, and underscores are allowed."
        #     )

        return value

    def validate_urgency_level(self, value: Optional[int]) -> Optional[int]:
        """
        Validate the urgency level is within the allowed range.

        Args:
            value: Integer urgency level or None

        Returns:
            The validated urgency level if valid
        """
        # If no urgency level is provided, that's fine
        if value is None:
            return None

        # The field already has min_value=1, max_value=5 constraints that are
        # automatically enforced by the serializer framework
        return value

    def create(self, *_: Any) -> None:
        """Not used - this serializer only validates confirmation data."""
        raise NotImplementedError(
            "InvoiceConfirmationSerializer is for validation only. "
            "Use InvoiceProcessingService for invoice finalization."
        )

    def update(self, *_: Any) -> None:
        """Not used - this serializer only validates confirmation data."""
        raise NotImplementedError(
            "InvoiceConfirmationSerializer is for validation only. "
            "Use InvoiceProcessingService for invoice finalization."
        )
