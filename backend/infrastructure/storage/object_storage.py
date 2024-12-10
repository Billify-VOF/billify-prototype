"""
Cloud storage implementation using Digital Ocean Spaces.

This module provides a production-ready storage solution for invoice files
using Digital Ocean Spaces (compatible with S3). It handles secure file
storage, retrieval, and URL generation while maintaining proper file
organization and access control.
"""

from pathlib import Path
import uuid
from datetime import datetime
from domain.exceptions import StorageError
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class ObjectStorage:
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
                's3',
                region_name=settings.AWS_S3_REGION_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        except Exception as e:
            msg = f"Failed to initialize cloud storage: {str(e)}"
            raise StorageError(msg) from e

    def save_invoice(self, file) -> str:
        """
        Save an invoice file to cloud storage with proper organization.

        Args:
            file: The invoice file to store

        Returns:
            str: The storage path where the file was saved

        Raises:
            StorageError: If the file cannot be saved
        """
        try:
            # Generate a structured storage path for better organization
            year_month = datetime.now().strftime('%Y/%m')
            filename = self._generate_unique_filename(file.name)
            storage_path = f"invoices/{year_month}/{filename}"

            # Upload to Digital Ocean Spaces
            self.client.upload_fileobj(
                file,
                self.bucket,
                storage_path,
                ExtraArgs={'ACL': 'private'}
            )

            return storage_path

        except ClientError as e:
            msg = f"Cloud storage operation failed: {str(e)}"
            raise StorageError(msg) from e
        except Exception as e:
            msg = f"Unexpected storage error: {str(e)}"
            raise StorageError(msg) from e

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
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': storage_path
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            msg = f"Failed to generate file URL: {str(e)}"
            raise StorageError(msg) from e

    def _generate_unique_filename(self, original_name: str) -> str:
        """Create unique filename while preserving the original extension."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        ext = Path(original_name).suffix
        return f"{timestamp}_{unique_id}{ext}"
