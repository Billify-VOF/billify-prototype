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
from domain.repositories.interfaces.storage_repository import StorageRepository
from django.core.files.uploadedfile import UploadedFile
from typing import Union, BinaryIO


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
                region_name=settings.AWS_S3_REGION_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        except Exception as e:
            msg = f"Failed to initialize cloud storage: {str(e)}"
            raise StorageError(msg) from e

    def save_file(self, file: Union[BinaryIO, UploadedFile], identifier: str) -> str:
        try:
            year_month = datetime.now().strftime("%Y/%m")
            # Get filename safely with fallback
            file_name = getattr(file, "name", None)
            ext = Path(file_name or "").suffix or ".pdf"
            storage_path = f"invoices/{year_month}/{identifier}{ext}"

            self.client.upload_fileobj(
                file, self.bucket, storage_path, ExtraArgs={"ACL": "private"}
            )

            return storage_path
        except Exception as e:
            raise StorageError(f"Failed to save file: {str(e)}") from e

    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Generate a pre-signed URL for temporary file access.

        Args:
            storage_path: Path to the file in storage
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Pre-signed URL for file access

        Raises:
            StorageError: If URL generation fails
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": storage_path},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            msg = f"Failed to generate file URL: {str(e)}"
            raise StorageError(msg) from e

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
            # Convert S3 path to a Path object
            return Path(identifier)
        except Exception as e:
            raise StorageError(f"Failed to get file path: {str(e)}") from e

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
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}") from e
