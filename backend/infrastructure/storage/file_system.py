"""File system implementation for invoice storage.

This module provides concrete implementation for storing invoice
files in the local file system, following our storage interface
contract.
"""
from pathlib import Path
from datetime import datetime
from django.conf import settings
from domain.exceptions import StorageError
from domain.repositories.interfaces.storage_repository import StorageRepository
from django.core.files.uploadedfile import UploadedFile


class FileStorage(StorageRepository):
    """Handles file storage operations using the local file system."""

    def __init__(self):
        """Initialize storage with base directory for invoices."""
        # Use Django's MEDIA_ROOT setting
        self.base_dir = Path(settings.MEDIA_ROOT) / 'invoices'
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadedFile, identifier: str) -> str:
        """
        Save an invoice file to the storage system with organized structure.

        Args:
            file: The invoice file to store
            identifier: The identifier for the file

        Returns:
            str: The relative path where the file was stored (for db storage)

        Raises:
            StorageError: If the file cannot be saved
        """
        try:
            # Create year/month directory structure
            year_month = datetime.now().strftime('%Y/%m')
            storage_dir = self.base_dir / year_month
            print(f"Creating directory at: {storage_dir}")
            storage_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename while preserving original extension
            original_name = Path(file.name)
            file_path = storage_dir / f"{identifier}{original_name.suffix}"
            print(f"Generated filename: {file_path}")

            # Save the file using chunks for memory efficiency
            with file_path.open('wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            print(f"File saved successfully at: {file_path}")

            # Return path relative to base_dir for database storage
            relative_path = str(file_path.relative_to(self.base_dir))
            print(f"Relative path: {relative_path}")
            return relative_path

        except Exception as e:
            raise StorageError(
                f"Failed to save file: {str(e)}"
            ) from e

    def get_file_path(self, relative_path: str) -> Path:
        """
        Get the full system path for a stored file.

        Args:
            relative_path: The path relative to base_dir (as stored in db)

        Returns:
            Path: Full system path to the file
        """
        full_path = self.base_dir / relative_path
        print(f"Looking for file at: {full_path}")
        print(f"get_file_path called with: {relative_path}")
        print(f"Returning full path: {full_path}")
        return full_path

    def delete_file(self, file_path: str) -> None:
        """
        Delete a stored file.

        Args:
            file_path: Relative path to the file from base_dir

        Raises:
            StorageError: If file deletion fails
        """
        try:
            full_path = self.base_dir / file_path
            if full_path.exists():
                full_path.unlink()
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}") from e
