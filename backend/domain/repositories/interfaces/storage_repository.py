from abc import ABC, abstractmethod
from typing import BinaryIO
from pathlib import Path


class StorageRepository(ABC):
    """
    Abstract interface for file storage operations.

    This repository defines the contract for storing and retrieving files,
    independent of the actual storage implementation (filesystem, cloud, etc.).

    The interface is designed to be:
    1. Storage-agnostic (works with any storage backend)
    2. File-type agnostic (can store any type of file)
    3. Focused purely on storage operations
    """

    @abstractmethod
    def save_file(self, file: BinaryIO, identifier: str) -> str:
        """
        Save a file to storage and return its path/identifier.

        Args:
            file: The file object to store
            identifier: Unique identifier for the file (e.g., 'invoice_123')

        Returns:
            str: Storage path or identifier for future retrieval

        Raises:
            StorageError: If file cannot be saved
        """
        pass

    @abstractmethod
    def get_file_path(self, identifier: str) -> Path:
        """
        Get the full path to a stored file.

        Args:
            identifier: The storage identifier returned by save_file

        Returns:
            Path: Full path to the file

        Raises:
            StorageError: If file cannot be found
        """
        pass

    @abstractmethod
    def delete_file(self, identifier: str) -> None:
        """
        Delete a stored file.

        Args:
            identifier: The storage identifier returned by save_file

        Raises:
            StorageError: If file cannot be deleted
        """
        pass
