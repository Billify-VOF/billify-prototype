"""File system implementation for invoice storage.

This module provides concrete implementation for storing invoice
files in the local file system, following DDD principles with
clear separation of concerns.
"""
from pathlib import Path
from datetime import datetime
from django.conf import settings
from domain.exceptions import StorageError
from domain.repositories.interfaces.storage_repository import (
    StorageRepository,
)
from django.core.files.uploadedfile import UploadedFile
from logging import getLogger
from typing import BinaryIO, Union, Optional, Tuple
import shutil

# Module-level logger
logger = getLogger(__name__)


class FileStorageService:
    """Service for handling file system operations.

    This service encapsulates the infrastructure concerns (file I/O operations)
    separate from the repository responsibilities, adhering to DDD principles.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize service with base directory for file storage.

        Args:
            base_dir: Base directory for storage. Defaults to
                MEDIA_ROOT/invoices
        """
        # Use Django's MEDIA_ROOT setting if no base_dir provided
        self.base_dir = base_dir or Path(settings.MEDIA_ROOT) / "invoices"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Initialized FileStorageService with base_dir: %s", self.base_dir)

    def generate_storage_path(
        self, identifier: str, original_filename: Optional[str] = None
    ) -> Tuple[str, Path]:
        """Generate appropriate storage path based on identifier.

        This method centralizes path generation logic in the service layer.

        Args:
            identifier: Unique identifier for the file
            original_filename: Original filename to extract extension

        Returns:
            tuple[str, Path]: (relative_path, full_path)
        """
        # Create year/month directory structure
        year_month = datetime.now().strftime("%Y/%m")
        relative_dir = year_month

        # Handle file extension
        if original_filename:
            original_name = Path(original_filename)
            suffix = original_name.suffix
        else:
            suffix = ".pdf"  # Default extension

        # Create filename and paths
        filename = f"{identifier}{suffix}"
        relative_path = f"{relative_dir}/{filename}"
        full_path = self.base_dir / relative_path

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug("Generated storage path: %s", relative_path)
        return relative_path, full_path

    def write_file(self, file: Union[BinaryIO, UploadedFile], filepath: Path) -> None:
        """Write file contents to the specified path.

        Args:
            file: The file object to write
            filepath: Full path where file should be written

        Raises:
            StorageError: If file cannot be written
        """
        try:
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Save the file using chunks for memory efficiency
            with filepath.open("wb+") as destination:
                if hasattr(file, "chunks"):
                    # Django UploadedFile
                    for chunk in file.chunks():
                        destination.write(chunk)
                else:
                    # Standard BinaryIO
                    destination.write(file.read())

            logger.info("File written successfully to: %s", filepath)

        except Exception as e:
            logger.error("Failed to write file: %s", str(e))
            raise StorageError(f"Failed to write file: {str(e)}") from e

    def move_file(self, source_path: Path, target_path: Path) -> None:
        """Move a file from source to target path.

        This method handles the actual file system move operation.
        It is more efficient than copying and deleting as it uses
        the operating system's move (rename) functionality.

        Args:
            source_path: Full path to the source file
            target_path: Full path to the target destination

        Raises:
            StorageError: If the move operation fails
        """
        try:
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file using shutil.move which is more efficient
            # than a copy+delete operation
            shutil.move(str(source_path), str(target_path))

            logger.info("File moved successfully from %s to %s", source_path, target_path)

        except Exception as e:
            logger.error("Failed to move file: %s", str(e))
            raise StorageError(f"Failed to move file: {str(e)}") from e

    def delete_file(self, filepath: Path) -> None:
        """Delete a file from the file system.

        Args:
            filepath: Path to the file to delete

        Raises:
            StorageError: If file deletion fails
        """
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info("File deleted: %s", filepath)
            else:
                logger.warning("File not found for deletion: %s", filepath)

        except Exception as e:
            logger.error("Failed to delete file: %s", str(e))
            raise StorageError(f"Failed to delete file: {str(e)}") from e

    def get_full_path(self, relative_path: str) -> Path:
        """Convert a relative path to a full file system path.

        Args:
            relative_path: Path relative to base directory

        Returns:
            Path: Full system path to the file
        """
        return self.base_dir / relative_path


class FileStorage(StorageRepository):
    """Repository for file storage operations using the local file system.

    This class follows DDD principles by:
    1. Focusing on storage repository responsibilities (metadata)
    2. Delegating file I/O operations to FileStorageService
    3. Providing a clean domain-oriented interface
    """

    def __init__(self):
        """Initialize storage repository with service for file operations."""
        self.storage_service = FileStorageService()
        logger.debug("FileStorage repository initialized")

    def save_file(self, file: Union[BinaryIO, UploadedFile], identifier: str) -> str:
        """
        Save an invoice file to the storage system.

        This repository method focuses on managing the metadata aspects
        of file storage, delegating actual file I/O to the service layer.

        Args:
            file: The invoice file to store
            identifier: The identifier for the file

        Returns:
            str: The relative path where the file was stored (for db storage)

        Raises:
            StorageError: If the file cannot be saved
        """
        try:
            # Get file name if available (for extension)
            file_name = getattr(file, "name", None)

            # Use service to generate paths (service responsibility)
            relative_path, full_path = self.storage_service.generate_storage_path(identifier, file_name)

            # Delegate file writing to service (infrastructure concern)
            self.storage_service.write_file(file, full_path)

            # Return metadata (relative path) for database storage
            return relative_path

        except Exception as e:
            logger.error("Repository failed to save file: %s", str(e))
            raise StorageError(f"Failed to save file: {str(e)}") from e

    def move_file(self, source_identifier: str, target_identifier: str) -> str:
        """
        Move a file from one location to another within the storage system.

        This repository method handles moving files between locations,
        delegating the actual file I/O operations to the storage service.

        Args:
            source_identifier: The relative path of the source file
            target_identifier: The identifier to use for the target location

        Returns:
            str: New relative path for the moved file

        Raises:
            StorageError: If file cannot be moved
        """
        try:
            # Check if storage service is initialized
            if self.storage_service is None:
                raise StorageError("Storage service not initialized")

            # Get source full path from relative path
            source_full_path = self.storage_service.get_full_path(source_identifier)

            # Generate target path with the new identifier
            # Extract extension from the source file
            source_path = Path(source_identifier)
            file_name = source_path.name

            # Generate new storage path for the target
            (
                target_relative_path,
                target_full_path,
            ) = self.storage_service.generate_storage_path(target_identifier, file_name)

            # Delegate file moving to service (infrastructure concern)
            self.storage_service.move_file(source_full_path, target_full_path)

            # Return new relative path for database storage
            return target_relative_path

        except Exception as e:
            logger.error("Repository failed to move file: %s", str(e))
            raise StorageError(f"Failed to move file: {str(e)}") from e

    def get_file_path(self, relative_path: str) -> Path:
        """
        Get the full system path for a stored file.

        Repository method that translates metadata (relative path)
        to a concrete file location.

        Args:
            relative_path: The path relative to base_dir (as stored in db)

        Returns:
            Path: Full system path to the file
        """
        logger.debug("Getting file path for: %s", relative_path)
        return self.storage_service.get_full_path(relative_path)

    def delete_file(self, file_path: str) -> None:
        """
        Delete a stored file.

        Repository method that manages the deletion of a file
        based on its metadata (relative path).

        Args:
            file_path: Relative path to the file from base_dir

        Raises:
            StorageError: If file deletion fails
        """
        try:
            # Get full path from metadata (repository responsibility)
            full_path = self.storage_service.get_full_path(file_path)

            # Delegate deletion to service (infrastructure concern)
            self.storage_service.delete_file(full_path)

        except Exception as e:
            logger.error("Repository failed to delete file: %s", str(e))
            raise StorageError(f"Failed to delete file: {str(e)}") from e
