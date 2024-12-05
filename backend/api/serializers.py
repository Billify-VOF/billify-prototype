"""Serializers for the API application."""

from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """Serializer for PDF file uploads with size and type validation."""

    file = serializers.FileField()

    def validate_file(self, value):
        """Validate that uploaded file is a PDF and doesn't exceed 10MB."""
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        max_size = 10 * 1024 * 1024  # 10 MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size must not exceed {max_size / (1024 * 1024)}MB."
            )
        return value

    def create(self, *_):
        """
        This serializer does not handle object creation.
        """
        raise NotImplementedError(
            "FileUploadSerializer does not support object creation."
        )

    def update(self, *_):
        """
        This serializer does not handle object updates.
        """
        raise NotImplementedError(
            "FileUploadSerializer does not support object updates."
        )
