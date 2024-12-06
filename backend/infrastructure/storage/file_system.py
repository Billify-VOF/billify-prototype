"""File system implementation for invoice storage.

This module provides concrete implementation for storing invoice
files in the local file system, following our storage interface
contract.
"""
from pathlib import Path
from domain.exceptions import StorageError


class FileStorage:
    """Handles file storage operations using the local file system."""

    def __init__(self):
        """Initialize storage with base directory for invoices."""
        self.base_dir = Path('media/invoices')
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_invoice(self, file):
        """
        Save an invoice file to the storage system.

        Args:
            file: The invoice file to store

        Returns:
            str: The path where the file was stored

        Raises:
            StorageError: If the file cannot be saved
        """
        try:
            # Create a unique filename
            file_path = self.base_dir / file.name

            # Save the file
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            return str(file_path)

        except Exception as e:
            raise StorageError(
                f"Failed to save invoice: {str(e)}"
            ) from e
