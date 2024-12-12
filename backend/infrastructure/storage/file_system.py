"""File system implementation for invoice storage.

This module provides concrete implementation for storing invoice
files in the local file system, following our storage interface
contract.
"""
from pathlib import Path
from datetime import datetime
import uuid
from domain.exceptions import StorageError


class FileStorage:
    """Handles file storage operations using the local file system."""

    def __init__(self):
        """Initialize storage with base directory for invoices."""
        # Using absolute path from project root ensures consistent behavior
        self.base_dir = Path('media/invoices')
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_invoice(self, file):
        """
        Save an invoice file to the storage system with organized structure.

        Args:
            file: The invoice file to store

        Returns:
            str: The relative path where the file was stored (for db storage)

        Raises:
            StorageError: If the file cannot be saved
        """
        try:
            # Create year/month directory structure
            year_month = datetime.now().strftime('%Y/%m')
            storage_dir = self.base_dir / year_month
            storage_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename while preserving original extension
            original_name = Path(file.name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:8]
            unique_filename = f"{timestamp}_{unique_id}{original_name.suffix}"

            # Create full storage path
            file_path = storage_dir / unique_filename

            # Save the file using chunks for memory efficiency
            with file_path.open('wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Return path relative to base_dir for database storage
            return str(file_path.relative_to(self.base_dir))

        except Exception as e:
            raise StorageError(
                f"Failed to save invoice: {str(e)}"
            ) from e

    def get_file_path(self, relative_path: str) -> Path:
        """
        Get the full system path for a stored file.

        Args:
            relative_path: The path relative to base_dir (as stored in db)

        Returns:
            Path: Full system path to the file
        """
        return self.base_dir / relative_path
