"""Temporary storage management for file operations.

This module provides an adapter for handling temporary file storage,
with functionality for tracking expiration and promoting files to
permanent storage when needed.
"""
from pathlib import Path
from typing import Dict, List, Optional, BinaryIO, Any
from datetime import datetime, timedelta
import json
import uuid

from django.conf import settings
from django.utils import timezone
from logging import getLogger
from filelock import FileLock  # Import filelock for thread-safe file access

from domain.exceptions import StorageError
from domain.repositories.interfaces.storage_repository import StorageRepository

# Module-level logger
logger = getLogger(__name__)


class TemporaryStorageAdapter:
    """Adapter for managing temporary file storage.

    This class adapts any StorageRepository implementation to provide
    temporary file storage capabilities while maintaining separation of concerns.
    It uses composition to delegate storage operations to the repository.
    """

    def __init__(
        self,
        storage_repository: StorageRepository,
        expiration_hours: int = 24,
        registry_path: Optional[Path] = None,
    ):
        """Initialize the temporary storage adapter.

        Args:
            storage_repository: The storage repository to delegate operations to
            expiration_hours: Number of hours before temporary files expire
            registry_path: Optional custom path for the registry file
        """
        # Store the repository for delegation
        self.storage_repository = storage_repository
        self.expiration_hours = expiration_hours

        # Set up registry file for tracking temporary files
        self.registry_path = registry_path or (
            Path(settings.MEDIA_ROOT) / "temp_registry.json"
        )

        # Set up lock file path
        self.lock_file_path = Path(str(self.registry_path) + ".lock")

        # Initialize registry if it doesn't exist
        with FileLock(self.lock_file_path):
            if not self.registry_path.exists():
                # Ensure directory exists
                self.registry_path.parent.mkdir(parents=True, exist_ok=True)

                # Create empty registry
                with self.registry_path.open("w") as f:
                    json.dump({}, f)

                logger.debug(
                    "Created new temporary file registry at %s", self.registry_path
                )

        logger.debug(
            "Initialized TemporaryStorageAdapter with expiration: %s hours, registry: %s",
            self.expiration_hours,
            self.registry_path,
        )

    def store_temporary(self, file: BinaryIO, identifier: str) -> str:
        """Store a file temporarily with automatic expiration.

        This method:
        1. Creates a unique temporary identifier
        2. Stores the file using the underlying repository
        3. Tracks the file for expiration

        Args:
            file: The file to store (binary file-like object)
            identifier: Base identifier for the file

        Returns:
            str: Relative path where the file was stored

        Raises:
            StorageError: If the file cannot be saved or tracked
        """
        # Generate a unique temporary identifier with timestamp and random suffix
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        random_suffix = uuid.uuid4().hex[
            :8
        ]  # Use 8 characters from a UUID for uniqueness
        temp_identifier = f"temp_{identifier}_{timestamp}_{random_suffix}"

        try:
            # Delegate file storage to the underlying repository
            relative_path = self.storage_repository.save_file(file, temp_identifier)

            # Track the file in our registry for expiration
            # Try multiple times to track the file to avoid orphaned files
            max_tracking_attempts = 3
            tracking_success = False

            for attempt in range(1, max_tracking_attempts + 1):
                if self._track_temporary_file(relative_path, timezone.now()):
                    tracking_success = True
                    break
                logger.warning(
                    "Attempt %d/%d: Failed to track temporary file %s in registry, retrying...",
                    attempt,
                    max_tracking_attempts,
                    relative_path,
                )

            # If tracking still failed after retries, clean up to avoid orphaned files
            if not tracking_success:
                logger.error(
                    "Failed to track file %s in registry after %d attempts. Cleaning up to avoid orphaned files.",
                    relative_path,
                    max_tracking_attempts,
                )
                try:
                    # Delete the file since we can't track it
                    self.storage_repository.delete_file(relative_path)
                    raise StorageError(
                        f"Failed to store temporary file: Could not track in registry after {max_tracking_attempts} attempts"
                    )
                except Exception as cleanup_error:
                    # If cleanup also fails, report both errors
                    logger.error(
                        "Failed to clean up untracked file: %s", str(cleanup_error)
                    )
                    raise StorageError(
                        f"Failed to store temporary file: Could not track in registry and cleanup failed"
                    )

            logger.info(
                "Stored temporary file at %s (expires in %d hours)",
                relative_path,
                self.expiration_hours,
            )

            return relative_path

        except Exception as e:
            logger.error("Failed to store temporary file: %s", str(e))
            raise StorageError(f"Failed to store temporary file: {str(e)}") from e

    def promote_to_permanent(self, temp_path: str, permanent_identifier: str) -> str:
        """Move a temporary file to permanent storage.

        This method handles the second phase of the two-phase storage approach:
        1. Verify the file exists and is in the registry
        2. Move the file to its permanent location
        3. Remove it from the temporary registry

        Args:
            temp_path: Relative path to the temporary file
            permanent_identifier: Identifier to use for permanent storage

        Returns:
            str: New relative path in permanent storage

        Raises:
            StorageError: If the file cannot be moved or doesn't exist
        """
        # Check if the file exists in our registry
        registry = self._load_registry()

        if temp_path not in registry:
            logger.warning(
                "Attempting to promote untracked temporary file: %s", temp_path
            )
            # Continue anyway - it might be a valid file that wasn't tracked properly

        try:
            # Use the repository's move_file method to handle the actual move
            permanent_path = self.storage_repository.move_file(
                temp_path, permanent_identifier
            )

            # Remove from the temporary registry
            self._untrack_temporary_file(temp_path)

            logger.info(
                "Promoted temporary file from %s to permanent location %s",
                temp_path,
                permanent_path,
            )

            return permanent_path

        except Exception as e:
            logger.error(
                "Failed to promote temporary file %s to permanent: %s",
                temp_path,
                str(e),
            )
            raise StorageError(
                f"Failed to promote temporary file to permanent: {str(e)}"
            ) from e

    def cleanup_expired(self) -> Dict[str, Any]:
        """Remove all temporary files that have exceeded their expiration time.

        This method:
        1. Identifies all expired files using _get_expired_files
        2. Deletes each file from the storage system
        3. Removes the tracking info from the registry
        4. Returns statistics about the cleanup operation

        Returns:
            Dict[str, Any]: Statistics about the cleanup operation including:
                - files_removed: Number of files successfully removed
                - files_failed: Number of files that failed to be removed
                - bytes_reclaimed: Approximate storage space reclaimed (if available)
                - registry_inconsistencies: Number of files that couldn't be untracked

        Raises:
            StorageError: If there's a critical error accessing the registry
        """
        cleanup_stats = {
            "files_removed": 0,
            "files_failed": 0,
            "bytes_reclaimed": 0,
            "registry_inconsistencies": 0,  # Track registry inconsistencies
        }

        try:
            # Get all expired files
            expired_files = self._get_expired_files()

            if not expired_files:
                logger.info("No expired temporary files found during cleanup")
                return cleanup_stats

            logger.info(
                "Found %d expired temporary files to clean up", len(expired_files)
            )

            # Process each expired file
            for file_path in expired_files:
                file_size = 0
                deletion_successful = False

                try:
                    # Try to get file size before deletion (for statistics)
                    try:
                        full_path = self.storage_repository.get_file_path(file_path)
                        if full_path and full_path.exists():
                            file_size = full_path.stat().st_size
                    except Exception:
                        # Non-critical error, just continue without size info
                        pass

                    # Delete the file
                    self.storage_repository.delete_file(file_path)
                    deletion_successful = True  # Mark deletion as successful

                    # Update statistics for successfully deleted files
                    cleanup_stats["files_removed"] += 1
                    cleanup_stats["bytes_reclaimed"] += file_size
                    logger.debug("Removed expired temporary file: %s", file_path)

                except Exception as e:
                    deletion_successful = False  # Explicitly mark deletion as failed
                    cleanup_stats["files_failed"] += 1
                    logger.warning(
                        "Failed to remove expired temporary file %s: %s",
                        file_path,
                        str(e),
                    )

                # Only attempt to untrack if deletion was successful and track operation fails
                if deletion_successful and not self._untrack_temporary_file(file_path):
                    cleanup_stats["registry_inconsistencies"] = (
                        cleanup_stats.get("registry_inconsistencies", 0) + 1
                    )
                    logger.warning(
                        "File was deleted but could not be untracked from registry: %s",
                        file_path,
                    )

            if cleanup_stats.get("registry_inconsistencies", 0) > 0:
                logger.warning(
                    "%d files were deleted but could not be untracked from the registry",
                    cleanup_stats.get("registry_inconsistencies", 0),
                )

            logger.info(
                "Cleanup complete: removed %d files, failed to remove %d files, "
                "reclaimed approximately %d bytes, registry inconsistencies: %d",
                cleanup_stats.get("files_removed", 0),
                cleanup_stats.get("files_failed", 0),
                cleanup_stats.get("bytes_reclaimed", 0),
                cleanup_stats.get("registry_inconsistencies", 0),
            )

            return cleanup_stats

        except Exception as e:
            logger.error("Critical error during temporary file cleanup: %s", str(e))
            raise StorageError(
                f"Failed to clean up expired temporary files: {str(e)}"
            ) from e

    def _load_registry(self) -> Dict:
        """Load the temporary file registry from disk.

        This method reads the registry JSON file and returns its contents.
        If the file doesn't exist or is invalid, it returns an empty dict.

        Returns:
            Dict: Dictionary mapping file paths to their metadata
        """
        try:
            with FileLock(self.lock_file_path):
                if not self.registry_path.exists():
                    logger.warning(
                        "Registry file not found at %s, returning empty registry",
                        self.registry_path,
                    )
                    return {}

                with self.registry_path.open("r") as f:
                    registry = json.load(f)
                    logger.debug("Loaded registry with %d entries", len(registry))
                    return registry

        except json.JSONDecodeError as e:
            logger.error("Failed to parse registry file as JSON: %s", str(e))
            return {}

        except Exception as e:
            logger.error("Unexpected error loading registry file: %s", str(e))
            return {}

    def _save_registry(self, registry: Dict) -> None:
        """Save the registry dictionary to disk.

        Args:
            registry: Dictionary mapping file paths to their metadata

        Raises:
            StorageError: If the registry cannot be saved
        """
        try:
            with FileLock(self.lock_file_path):
                # Ensure parent directory exists
                self.registry_path.parent.mkdir(parents=True, exist_ok=True)

                # Write the registry to file with pretty formatting for readability
                with self.registry_path.open("w") as f:
                    json.dump(registry, f, indent=2)

                logger.debug("Saved registry with %d entries", len(registry))

        except Exception as e:
            logger.error("Failed to save registry file: %s", str(e))
            raise StorageError(
                f"Failed to save temporary file registry: {str(e)}"
            ) from e

    def _track_temporary_file(self, path: str, creation_time: datetime) -> bool:
        """Add a file to the temporary registry.

        This method tracks a file in the registry with its creation time
        and calculates its expiration time based on the configured expiration hours.

        Args:
            path: Relative path to the file within the storage
            creation_time: When the file was created

        Returns:
            bool: True if the file was successfully tracked, False otherwise
        """
        try:
            # Load the current registry
            registry = self._load_registry()

            # Calculate expiration time
            expiration_time = creation_time + timedelta(hours=self.expiration_hours)

            # Add file to registry with metadata
            registry[path] = {
                "created_at": creation_time.isoformat(),
                "expires_at": expiration_time.isoformat(),
            }

            # Save updated registry
            try:
                self._save_registry(registry)
                logger.debug(
                    "Tracked temporary file %s, expires at %s",
                    path,
                    expiration_time.isoformat(),
                )
                return True
            except StorageError as e:
                logger.error(
                    "Failed to save registry after tracking file %s: %s", path, str(e)
                )
                return False

        except Exception as e:
            logger.error("Error tracking temporary file %s: %s", path, str(e))
            return False

    def _untrack_temporary_file(self, path: str) -> bool:
        """Remove a file from the temporary registry.

        This is typically called when a file is either:
        - Promoted to permanent storage
        - Deleted as part of cleanup
        - Manually removed

        Args:
            path: Relative path to the file to remove from tracking

        Returns:
            bool: True if the file was successfully untracked or wasn't tracked,
                  False if an error occurred
        """
        try:
            # Since we're using _load_registry and _save_registry which already have locks,
            # we don't need another lock here as those methods handle locking

            # Load the current registry
            registry = self._load_registry()

            # Check if the file is in the registry
            if path not in registry:
                logger.debug(
                    "File %s was not in the registry, nothing to untrack", path
                )
                return True  # Not an error, file just wasn't tracked

            # Remove the file from the registry
            file_info = registry.pop(path)

            # Save the updated registry
            try:
                self._save_registry(registry)
                created_at = file_info.get("created_at", "unknown")
                logger.debug(
                    "Untracked temporary file %s (created: %s)", path, created_at
                )
                return True
            except StorageError as e:
                logger.error(
                    "Failed to save registry after untracking file %s: %s", path, str(e)
                )
                return False

        except Exception as e:
            logger.error("Error untracking temporary file %s: %s", path, str(e))
            return False

    def _get_expired_files(self) -> List[str]:
        """Get a list of files that have exceeded their expiration time.

        This method scans the registry for files whose expiration timestamp
        is earlier than the current time.

        Returns:
            List[str]: List of file paths that have expired
        """
        try:
            # Load the registry (this will use the lock via _load_registry)
            registry = self._load_registry()

            # Get current time for comparison
            now = timezone.now()

            # Find expired files
            expired_files = []
            for path, info in registry.items():
                try:
                    # Parse expiration time from ISO format
                    expires_at = datetime.fromisoformat(info["expires_at"])

                    # Convert expires_at to timezone-aware if it's naive
                    if expires_at.tzinfo is None:
                        expires_at = timezone.make_aware(expires_at)

                    # Check if expired
                    if now > expires_at:
                        expired_files.append(path)
                        logger.debug(
                            "File %s expired at %s (now: %s)",
                            path,
                            expires_at.isoformat(),
                            now.isoformat(),
                        )
                except (KeyError, ValueError) as e:
                    # Handle missing or invalid timestamps
                    logger.warning(
                        "Invalid expiration data for file %s: %s", path, str(e)
                    )

            if expired_files:
                logger.info("Found %d expired files", len(expired_files))
            else:
                logger.debug("No expired files found")

            return expired_files

        except json.JSONDecodeError as e:
            # Handle JSON parsing errors separately (more specific exception first)
            logger.error("Failed to parse registry JSON: %s", str(e))
            return []
        except (KeyError, FileNotFoundError, PermissionError) as e:
            # Handle file access and data structure errors
            logger.error("Error accessing registry: %s", str(e))
            return []
        except ValueError as e:
            # Handle other value errors that aren't JSONDecodeError
            logger.error("Error parsing data in registry: %s", str(e))
            return []

    def is_expired(self, path: str) -> bool:
        """Check if a specific file has expired.

        Args:
            path: Relative path to the file

        Returns:
            bool: True if the file has expired or is not in registry, False otherwise
        """
        try:
            # Load the registry (this will use the lock via _load_registry)
            registry = self._load_registry()

            # Check if the file is in the registry
            if path not in registry:
                logger.debug(
                    "File %s is not in the registry, cannot determine expiration", path
                )
                return False

            # Get file info and parse expiration time
            file_info = registry[path]
            try:
                expires_at = datetime.fromisoformat(file_info["expires_at"])
            except (KeyError, ValueError) as e:
                logger.warning("Invalid expiration data for file %s: %s", path, str(e))
                return False

            # Convert expires_at to timezone-aware if it's naive
            if expires_at.tzinfo is None:
                expires_at = timezone.make_aware(expires_at)

            # Check if expired
            now = timezone.now()
            is_expired = now > expires_at

            if is_expired:
                logger.debug(
                    "File %s has expired (expired at: %s, now: %s)",
                    path,
                    expires_at.isoformat(),
                    now.isoformat(),
                )
            else:
                logger.debug(
                    "File %s has not expired yet (expires at: %s, now: %s)",
                    path,
                    expires_at.isoformat(),
                    now.isoformat(),
                )

            return is_expired

        except Exception as e:
            logger.error("Error checking expiration for file %s: %s", path, str(e))
            return False
