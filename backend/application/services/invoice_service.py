"""Application service for invoice processing workflows.

This service orchestrates the overall invoice processing workflow,
coordinating between domain services, repositories and infrastructure
components.
"""

import os
import mimetypes
import contextlib
from pathlib import Path
from datetime import datetime
from domain.exceptions import ProcessingError, StorageError
from domain.repositories.interfaces.invoice_repository import InvoiceRepository
from domain.repositories.interfaces.storage_repository import StorageRepository
from domain.repositories.interfaces.account_repository import AccountRepository
from domain.services.invoice_service import InvoiceService
from integrations.transformers.pdf.transformer import (
    PDFTransformer,
    PDFTransformationError,
)
from logging import getLogger
from typing import BinaryIO, Dict, Any, Optional
from domain.models.value_objects import UrgencyLevel
from infrastructure.storage.temporary_storage import TemporaryStorageAdapter
from domain.exceptions import InvalidInvoiceError
import inspect
from io import BytesIO
import json

# Module-level logger
logger = getLogger(__name__)


class InvoiceProcessingService:
    """Application service that orchestrates invoice processing workflows.

    This service:
    - Handles the file storage aspects
    - Coordinates PDF transformation
    - Delegates to domain services for business logic
    - Manages transaction boundaries
    - Handles technical/infrastructure concerns
    """

    def __init__(
        self,
        invoice_service: InvoiceService,
        invoice_repository: InvoiceRepository,
        storage_repository: StorageRepository,
        account_repository: Optional[AccountRepository] = None,
    ) -> None:
        """Initialize service with required components.

        Args:
            invoice_service: Domain service for invoice business logic
            invoice_repository: Repository for invoice persistence
            storage_repository: Repository for file storage
            account_repository: Repository for account validation (optional)

        These dependencies are stored as instance attributes, allowing each
        instance of InvoiceProcessingService to have its own set of dependencies.
        This supports proper dependency injection and enables testing with mock objects.
        """
        self.invoice_service = invoice_service
        self.invoice_repository = invoice_repository
        self.storage_repository = storage_repository
        self.account_repository = account_repository
        self.pdf_transformer = PDFTransformer()
        self.temp_storage = TemporaryStorageAdapter(storage_repository)

    def _get_nested_attr(self, obj, attr_path, default=None):
        """Safely get a nested attribute or return default if not found."""
        current = obj
        for attr in attr_path.split("."):
            if not hasattr(current, attr):
                return default
            current = getattr(current, attr)
        return current

    def process_invoice(self, file: BinaryIO, user_id: int) -> Dict[str, Any]:
        """Process a new invoice file through the complete workflow.

        This application service method:
        1. Handles file storage
        2. Coordinates PDF transformation and metadata extraction
        3. Delegates to domain services for business rules
        4. Manages persistence through repositories
        5. Extracts and processes file and invoice metadata

        Args:
            file: The uploaded invoice file (binary file-like object)
            user_id: The ID of the user who uploaded the invoice

        Returns:
            Dict containing the processed invoice information, including:
            - invoice_id: Unique identifier of the saved invoice
            - invoice_number: Business identifier of the invoice
            - status: Current status of the invoice
            - file_path: Path where the file is stored
            - buyer/seller information: Extracted from the invoice
            - payment details: Method, currency, amounts, etc.
            - file metadata: Size, type, original filename
            - urgency: Information about invoice processing priority

        Raises:
            ProcessingError: For failures during processing
            StorageError: For failures storing the file
        """
        logger.info("Starting invoice processing for user_id=%s", user_id)
        try:
            # Generate unique identifier for file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            identifier = f"invoice_{user_id}_{timestamp}"
            logger.debug("Generated identifier: %s", identifier)

            # Store file using storage repository
            logger.info("Saving invoice file to storage")
            file_path = self.storage_repository.save_file(file, identifier)
            full_path = self.storage_repository.get_file_path(file_path)
            logger.debug("File saved at path: %s", full_path)

            # Extract file metadata
            logger.info("Extracting file metadata")
            file_size = os.path.getsize(full_path)
            file_type = mimetypes.guess_type(full_path)[0] or "unknown"
            original_file_name = file.name
            logger.debug(
                "File metadata: size=%s bytes, type=%s, name=%s", file_size, file_type, original_file_name
            )

            # Extract data from PDF
            logger.info("Starting PDF transformation to extract invoice data")
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            if invoice_data.get("invoice_number"):
                logger.info(
                    "PDF transformation successful for invoice number: %s", invoice_data.get("invoice_number")
                )
            else:
                logger.warning("PDF transformation completed but no invoice number found")
            logger.debug("Extracted invoice data: %s", invoice_data)

            # Extract structured metadata
            logger.info("Extracting structured metadata from invoice data")
            invoice_metadata = {
                "buyer_name": invoice_data.get("buyer_name"),
                "buyer_address": invoice_data.get("buyer_address"),
                "buyer_email": invoice_data.get("buyer_email"),
                "buyer_vat": invoice_data.get("buyer_vat"),
                "seller_name": invoice_data.get("seller_name"),
                "seller_vat": invoice_data.get("seller_vat"),
                "payment_method": invoice_data.get("payment_method"),
                "currency": invoice_data.get("currency"),
                "iban": invoice_data.get("iban"),
                "bic": invoice_data.get("bic"),
                "payment_processor": invoice_data.get("payment_processor"),
                "transaction_id": invoice_data.get("transaction_id"),
                "subtotal": invoice_data.get("subtotal"),
                "vat_amount": invoice_data.get("vat_amount"),
                "total_amount": invoice_data.get("total_amount"),
            }
            logger.debug(
                "Structured metadata extracted: %s",
                {k: v for k, v in invoice_metadata.items() if v is not None},
            )

            # Delegate processing to domain service (avoid fetch-edit-save)
            logger.info("Delegating to domain service for invoice processing")
            saved_invoice = self.invoice_service.process_invoice(
                invoice_data=invoice_data,
                file_size=file_size,
                file_type=file_type,
                original_file_name=original_file_name,
                file_path=file_path,
                user_id=user_id,
            )
            logger.info("Invoice successfully processed and saved with ID: %s", saved_invoice.id)

            logger.info("Retrieving urgency information")
            urgency_info = self.invoice_service.get_urgency_info(saved_invoice)
            logger.debug("Urgency information: %s", urgency_info)

            # Invoice processing completed successfully
            updated = getattr(saved_invoice, "is_updated", False)
            logger.info("Invoice processing completed successfully")
            return {
                "invoice_id": saved_invoice.id,
                "invoice_number": saved_invoice.invoice_number,
                "status": saved_invoice.status,
                "file_path": file_path,
                "updated": updated,  # Use getattr to handle missing attribute
                **invoice_metadata,
                "file_size": file_size,
                "file_type": file_type,
                "original_file_name": original_file_name,
                "urgency": urgency_info,
            }

        except PDFTransformationError as e:
            logger.error("PDF transformation failed: %s", str(e), exc_info=True)

            # Log the attempt to clean up
            logger.info("Attempting to clean up file: %s", file_path)

            # Use contextlib.suppress for cleaner error handling
            # This is equivalent to try-except with a pass, but more explicit
            with contextlib.suppress(StorageError):
                self.storage_repository.delete_file(file_path)
                logger.info("File cleanup successful")

            # Include error type in message for better handling
            raise ProcessingError(f"PDF_TRANSFORMATION_ERROR: {str(e)}") from e

        except Exception as e:
            logger.error("Invoice processing failed: %s", str(e), exc_info=True)

            # Log the attempt to clean up
            logger.info("Attempting to clean up file: %s", file_path)

            # Use contextlib.suppress for cleaner error handling
            # This is equivalent to try-except with a pass, but more explicit
            with contextlib.suppress(StorageError):
                self.storage_repository.delete_file(file_path)
                logger.info("File cleanup successful")

            # Include more context about the error type
            error_type = type(e).__name__
            msg = f"Failed to process invoice ({error_type}): {str(e)}"
            raise ProcessingError(msg) from e

    def finalize_invoice(
        self,
        invoice_id: int,
        temp_file_path: str,
        urgency_level: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Finalize an invoice by transferring its file from temporary to permanent storage.

        This method:
        1. Validates the invoice exists and can be finalized
        2. Associates the specified urgency level with the invoice
        3. Transfers the file from temporary to permanent storage
        4. Updates the invoice record with the final storage path

        Args:
            invoice_id: ID of the invoice to finalize
            temp_file_path: Path to the temporary file
            urgency_level: Optional manual urgency level to set (1-5)
            user_id: ID of the user finalizing the invoice

        Returns:
            Dict containing the finalized invoice information, including:
            - invoice_id: Unique identifier of the finalized invoice
            - invoice_number: Business identifier of the invoice
            - status: Current status of the invoice
            - file_path: New permanent file path
            - urgency: Updated urgency information
            - timestamps: Creation and modification dates
            - metadata: Additional invoice details

        Raises:
            ProcessingError: For failures during finalization
            StorageError: For failures during file transfer
        """
        logger.info(
            "Starting invoice finalization for invoice_id=%s, user_id=%s", invoice_id, user_id or "unknown"
        )

        try:
            # Get the invoice from the repository
            invoice = self.invoice_repository.get_by_id(invoice_id)
            if not invoice:
                logger.error("Invoice not found with ID: %s", invoice_id)
                raise ProcessingError(f"Invoice not found: {invoice_id}")

            logger.info("Retrieved invoice: %s", invoice.invoice_number)

            # Validate the invoice data before finalizing
            try:
                invoice.validate()
                logger.debug("Invoice validation successful")
            except InvalidInvoiceError as e:
                logger.error("Invoice validation failed: %s", str(e))
                raise ProcessingError(f"Invalid invoice data: {str(e)}") from e

            # Generate unique identifier for permanent file using both invoice_number and user_id
            # for consistency with process_invoice method
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Determine effective user ID with proper validation
            effective_user_id = user_id or invoice.uploaded_by

            # Validate user exists in database if possible
            if effective_user_id and self.account_repository:
                valid_user = self.account_repository.find_by_id(effective_user_id)
                if not valid_user:
                    logger.warning(
                        "User ID %s does not exist in database for invoice %s. "
                        "Using ID for attribution but validation failed.",
                        effective_user_id,
                        invoice_id,
                    )
            elif not effective_user_id:
                # Default to system user if no ID provided
                effective_user_id = 1
                logger.warning(
                    "No valid user ID provided for invoice finalization (invoice_id=%s). "
                    "Using system user (ID=1) as fallback.",
                    invoice_id,
                )

            logger.info("Invoice being finalized by user ID: %s", effective_user_id)
            permanent_identifier = f"invoice_{invoice.invoice_number}_{effective_user_id}_{timestamp}"

            # Set urgency level if provided
            urgency = None
            if urgency_level is not None:
                # Validate urgency level first
                try:
                    urgency = UrgencyLevel.from_db_value(urgency_level)
                except (ValueError, TypeError) as e:
                    logger.warning("Invalid urgency level value: %s - %s", urgency_level, str(e))
                    # Continue with automatic urgency level
                else:
                    # Only set urgency if validation succeeded
                    invoice.set_urgency_manually(urgency)
                    logger.info("Set manual urgency level: %s", urgency.display_name)

            # Verify temporary file exists before attempting transfer
            temp_full_path = self.storage_repository.get_file_path(temp_file_path)
            if not temp_full_path.exists():
                logger.error("Temporary file not found: %s", temp_file_path)
                raise ProcessingError(f"Temporary file not found: {temp_file_path}")
            logger.debug("Verified temporary file exists: %s", temp_file_path)

            # Transfer the file to permanent storage
            try:
                logger.info("Transferring file from temporary to permanent storage")

                # Prepare metadata to associate with the stored file
                file_metadata = {
                    "invoice_id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "uploaded_by": str(effective_user_id),
                    "finalized_at": timestamp,
                }

                # Add urgency information to metadata if available
                if urgency:
                    file_metadata["urgency_level"] = str(urgency.value)
                    file_metadata["urgency_name"] = urgency.display_name

                # Add additional metadata from the invoice if available
                if hasattr(invoice, "amount") and invoice.amount is not None:
                    file_metadata["amount"] = str(invoice.amount)
                if hasattr(invoice, "due_date") and invoice.due_date is not None:
                    file_metadata["due_date"] = invoice.due_date.isoformat()
                if hasattr(invoice, "currency") and invoice.currency is not None:
                    file_metadata["currency"] = invoice.currency

                # Add buyer and seller information
                buyer_info = {}
                if self._get_nested_attr(invoice, "buyer.name"):
                    buyer_info["name"] = self._get_nested_attr(invoice, "buyer.name")
                if self._get_nested_attr(invoice, "buyer.vat"):
                    buyer_info["vat"] = self._get_nested_attr(invoice, "buyer.vat")

                seller_info = {}
                if self._get_nested_attr(invoice, "seller.name"):
                    seller_info["name"] = self._get_nested_attr(invoice, "seller.name")
                if self._get_nested_attr(invoice, "seller.vat"):
                    seller_info["vat"] = self._get_nested_attr(invoice, "seller.vat")

                # Convert dict values to strings for metadata compatibility
                if buyer_info:
                    buyer_info_str = {k: str(v) if v is not None else "" for k, v in buyer_info.items()}
                    file_metadata["buyer_info"] = json.dumps(buyer_info_str)
                if seller_info:
                    seller_info_str = {k: str(v) if v is not None else "" for k, v in seller_info.items()}
                    file_metadata["seller_info"] = json.dumps(seller_info_str)

                # Check if the storage repository is ObjectStorage and supports metadata
                if (
                    hasattr(self.storage_repository, "save_file")
                    and "metadata" in inspect.signature(self.storage_repository.save_file).parameters
                ):
                    logger.info("Storage repository supports metadata, using enhanced promotion")
                    # For repositories that support metadata (like ObjectStorage)
                    # We need to handle this differently as TemporaryStorageAdapter might not pass metadata through

                    # First read the file content
                    with open(temp_full_path, "rb") as file:
                        content = file.read()

                    # Save to permanent storage with metadata
                    file_obj = BytesIO(content)
                    # Add original filename to the file object
                    file_obj.name = Path(temp_file_path).name

                    # Save directly to permanent storage with metadata
                    permanent_path = self.storage_repository.save_file(
                        file_obj, permanent_identifier, metadata=file_metadata
                    )

                    # Delete the temporary file
                    self.temp_storage._untrack_temporary_file(temp_file_path)
                    self.storage_repository.delete_file(temp_file_path)
                else:
                    # Fall back to standard promotion if metadata not supported
                    logger.info("Using standard promotion mechanism")
                    permanent_path = self.temp_storage.promote_to_permanent(
                        temp_file_path, permanent_identifier
                    )

                    # If the storage repository is ObjectStorage but didn't have metadata in the signature,
                    # try to update metadata after promotion if the update_metadata method exists
                    if hasattr(self.storage_repository, "update_metadata"):
                        try:
                            logger.info("Updating metadata after promotion")
                            self.storage_repository.update_metadata(permanent_path, file_metadata)
                        except Exception as metadata_error:
                            logger.warning(
                                "Non-critical error: Failed to update metadata for %s: %s",
                                permanent_path,
                                str(metadata_error),
                            )

                logger.info("File transferred successfully to: %s", permanent_path)

                # Update invoice with the permanent file path
                invoice.file.path = permanent_path
                logger.debug("Updated invoice file path to: %s", permanent_path)

                # Save the updated invoice
                saved_invoice = self.invoice_repository.save(invoice, effective_user_id)
                logger.info("Invoice successfully finalized with ID: %s", saved_invoice.id)

                # Get urgency info
                urgency_info = self.invoice_service.get_urgency_info(saved_invoice)

                # Include comprehensive invoice details in the response
                return {
                    "invoice_id": saved_invoice.id,
                    "invoice_number": saved_invoice.invoice_number,
                    "status": saved_invoice.status,
                    "file_path": permanent_path,
                    "urgency": urgency_info,
                    "finalized": True,
                    # Additional details
                    "amount": (
                        str(self._get_nested_attr(saved_invoice, "amount"))
                        if self._get_nested_attr(saved_invoice, "amount")
                        else None
                    ),
                    "due_date": (
                        saved_invoice.due_date.isoformat()
                        if hasattr(saved_invoice, "due_date") and saved_invoice.due_date is not None
                        else None
                    ),
                    "timestamps": {
                        "created_at": getattr(saved_invoice, "created_at", None),
                        "updated_at": getattr(saved_invoice, "updated_at", None),
                    },
                    "buyer": {
                        "name": self._get_nested_attr(saved_invoice, "buyer.name"),
                        "address": self._get_nested_attr(saved_invoice, "buyer.address"),
                        "email": self._get_nested_attr(saved_invoice, "buyer.email"),
                        "vat": self._get_nested_attr(saved_invoice, "buyer.vat"),
                    },
                    "seller": {
                        "name": self._get_nested_attr(saved_invoice, "seller.name"),
                        "vat": self._get_nested_attr(saved_invoice, "seller.vat"),
                    },
                    "file_metadata": {
                        "size": self._get_nested_attr(saved_invoice, "file.size"),
                        "type": self._get_nested_attr(saved_invoice, "file.file_type"),
                        "original_name": self._get_nested_attr(saved_invoice, "file.original_name"),
                    },
                }

            except StorageError as e:
                logger.error("Storage error during finalization: %s", str(e))
                raise ProcessingError(f"Failed to transfer file to permanent storage: {str(e)}") from e

        except Exception as e:
            logger.error(
                "Invoice finalization failed: %s - invoice_id=%s, user_id=%s",
                str(e),
                invoice_id,
                user_id or "unknown",
                exc_info=True,
            )
            # Include more context about the error type
            error_type = type(e).__name__
            msg = f"Failed to finalize invoice ({error_type}): {str(e)}"
            raise ProcessingError(msg) from e
