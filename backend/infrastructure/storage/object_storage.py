"""
Cloud storage implementation using Digital Ocean Spaces.

This module provides a production-ready storage solution for invoice files
using Digital Ocean Spaces (compatible with S3). It handles secure file
storage, retrieval, and URL generation while maintaining proper file
organization and access control.
"""

from pathlib import Path
from datetime import datetime
from django.conf import settings
import boto3  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from domain.exceptions import StorageError
from domain.repositories.interfaces.storage_repository import (
    StorageRepository,
)
from django.core.files.uploadedfile import UploadedFile
from typing import Union, BinaryIO, Dict, Any, Optional
import json
import logging

# Module-level logger
logger = logging.getLogger(__name__)


class ObjectStorage(StorageRepository):
    """
    Manages file storage operations using Digital Ocean Spaces.

    This service handles all cloud storage operations, providing a consistent
    interface that matches our local storage implementation while adding
    cloud-specific features like pre-signed URLs and access control.
    """

    def __init__(self):
        """Initialize connection to Digital Ocean Spaces."""
        try:
            self.session = boto3.session.Session()
            self.client = self.session.client(
                "s3",
                region_name=settings.AWS_S3_REGION,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            self.bucket = settings.AWS_STORAGE_BUCKET_NAME
            logger.info("ObjectStorage initialized successfully for bucket: %s", self.bucket)
        except Exception as e:
            msg = f"Failed to initialize cloud storage: {str(e)}"
            logger.error(msg)
            raise StorageError(msg) from e

    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert metadata to S3-compatible format (all values must be strings).

        Args:
            metadata: Raw metadata with potentially complex values

        Returns:
            Dict with string values only, with complex data JSON-encoded
        """
        s3_metadata: Dict[str, str] = {}
        complex_data: Dict[str, Any] = {}

        # Separate simple values (convert to strings) from complex values
        for k, v in metadata.items():
            if v is None:
                continue

            if isinstance(v, (dict, list)):
                complex_data[k] = v
            else:
                s3_metadata[k] = str(v)

        # JSON encode complex values if present
        if complex_data:
            s3_metadata["complex_data"] = json.dumps(complex_data)

        return s3_metadata

    def save_file(
        self, file: str, identifier: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a file to Digital Ocean Spaces with associated metadata.

        Args:
            file: The file object to store
            identifier: Unique identifier for the file
            metadata: Optional metadata to associate with the file (e.g., urgency level)

        Returns:
            str: Storage path or identifier for future retrieval

        Raises:
            StorageError: If file cannot be saved
        """
        try:
            
            year_month = datetime.now().strftime("%Y/%m")
            # Get filename safely with fallback
            file_name = getattr(file, "name", None)
            ext = Path(file_name or "").suffix or ".pdf"
            storage_path = f"invoices/{year_month}/{identifier}{ext}"

            # Prepare upload parameters
            extra_args: Dict[str, Any] = {"ACL": "private"}

            # Add metadata if provided
            if metadata:
                s3_metadata = self._prepare_metadata(metadata)
                if s3_metadata:
                    extra_args["Metadata"] = s3_metadata
                    logger.debug("Uploading file with metadata: %s", s3_metadata)
            # Upload file
            self.client.upload_file(file, self.bucket, storage_path, ExtraArgs=extra_args)
            logger.info("File uploaded successfully to: %s", storage_path)

            return storage_path
        except Exception as e:
            error_msg = f"Failed to save file to object storage: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

    def get_file_metadata(self, storage_path: str) -> Dict[str, Any]:
        """
        Retrieve metadata associated with a stored file.

        Args:
            storage_path: Path to the file in storage

        Returns:
            Dict containing the file's metadata

        Raises:
            StorageError: If metadata retrieval fails
        """
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=storage_path)

            # Extract metadata from response
            metadata = dict(response.get("Metadata", {}))

            # Process complex metadata if it exists
            if "complex_data" in metadata:
                try:
                    complex_data = json.loads(metadata["complex_data"])
                    # Remove the complex_data field and merge the parsed data
                    del metadata["complex_data"]
                    metadata.update(complex_data)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse complex metadata for %s", storage_path)

            return metadata
        except ClientError as e:
            error_msg = f"Failed to retrieve metadata for {storage_path}: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

    def update_metadata(self, storage_path: str, metadata: Dict[str, Any]) -> None:
        """
        Update metadata for an existing file.

        Args:
            storage_path: Path to the file in storage
            metadata: New metadata to associate with the file

        Raises:
            StorageError: If metadata update fails
        """
        try:
            # Get current metadata to merge with new metadata
            current_metadata = self.get_file_metadata(storage_path)

            # Merge current and new metadata
            merged_metadata = {**current_metadata, **metadata}

            # Convert to S3-compatible format
            s3_metadata = self._prepare_metadata(merged_metadata)

            # Copy object to itself to update metadata
            self.client.copy_object(
                Bucket=self.bucket,
                CopySource=f"{self.bucket}/{storage_path}",
                Key=storage_path,
                Metadata=s3_metadata,
                MetadataDirective="REPLACE",
            )

            logger.info("Updated metadata for %s", storage_path)
        except Exception as e:
            error_msg = f"Failed to update metadata for {storage_path}: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Generate a pre-signed URL for secure temporary file access.

        Args:
            storage_path: Path to the file in storage
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Pre-signed URL for file access

        Raises:
            StorageError: If URL generation fails
        """
        try:
            # Add additional security parameters for the URL
            params = {
                "Bucket": self.bucket,
                "Key": storage_path,
                "ResponseContentDisposition": f'inline; filename="{Path(storage_path).name}"',
            }

            # Generate secure pre-signed URL with expiration
            url = self.client.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expires_in,
            )

            logger.debug("Generated pre-signed URL for %s (expires in %d seconds)", storage_path, expires_in)
            return url
        except ClientError as e:
            error_msg = f"Failed to generate file URL: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

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
        try:
            # Validate file exists in storage
            self.client.head_object(Bucket=self.bucket, Key=identifier)
            # Convert S3 path to a Path object
            return Path(identifier)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                error_msg = f"File not found in storage: {identifier}"
            else:
                error_msg = f"Failed to get file path: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get file path: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

    def delete_file(self, identifier: str) -> None:
        """
        Delete a stored file.

        Args:
            identifier: The storage identifier returned by save_file

        Raises:
            StorageError: If file cannot be deleted
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=identifier)
            logger.info("File deleted successfully: %s", identifier)
        except Exception as e:
            error_msg = f"Failed to delete file: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

    def move_file(self, source_identifier: str, target_identifier: str) -> str:
        """
        Move a file from one location to another within the storage system.

        Args:
            source_identifier: The identifier of the source file
            target_identifier: The identifier to use for the target location

        Returns:
            str: New storage identifier for the moved file

        Raises:
            StorageError: If file cannot be moved
        """
        try:
            # Extract file extension from source
            source_ext = Path(source_identifier).suffix

            # Generate timestamp-based path with the target identifier
            year_month = datetime.now().strftime("%Y/%m")
            target_path = f"invoices/{year_month}/{target_identifier}{source_ext}"

            # Copy the file to the new location with its metadata
            copy_source = {"Bucket": self.bucket, "Key": source_identifier}
            self.client.copy(CopySource=copy_source, Bucket=self.bucket, Key=target_path)

            # Delete the original file
            self.client.delete_object(Bucket=self.bucket, Key=source_identifier)

            logger.info("File moved from %s to %s", source_identifier, target_path)
            return target_path
        except Exception as e:
            error_msg = f"Failed to move file: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
