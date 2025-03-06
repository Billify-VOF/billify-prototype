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

    @abstractmethod
    def move_file(self, source_identifier: str, target_identifier: str) -> str:
        """
        Move a file from one location to another within the storage system.
        
        This operation should be atomic and implemented efficiently by the
        storage backend when possible (e.g., rename rather than copy+delete).
        
        Concurrency guarantees:
        - Atomicity: The operation should appear as a single indivisible action from the 
          perspective of other processes/threads. Implementations should ensure that:
            * Within a single filesystem: Use native rename operations where available
            * Across different storage systems: Either complete entirely or not at all
            * On failure: No partial state should be visible (either old or new location exists)
        - Visibility: Upon successful return, the file should be accessible at the new location
          and completely unavailable at the old location
        - Implementation note: Some storage systems may not support true atomic moves across
          different volumes or storage types. In these cases, implementers should document
          any limitations and potential race conditions.
        
        Args:
            source_identifier: The identifier of the source file
            target_identifier: The identifier to use for the target location
        
        Returns:
            str: New storage identifier for the moved file
        
        Raises:
            StorageError: If file cannot be moved
        """
        pass
