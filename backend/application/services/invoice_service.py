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
    ) -> None:
        """Initialize service with required components.

        Args:
            invoice_service: Domain service for invoice business logic
            invoice_repository: Repository for invoice persistence
            storage_repository: Repository for file storage

        These dependencies are stored as instance attributes, allowing each
        instance of InvoiceProcessingService to have its own set of dependencies.
        This supports proper dependency injection and enables testing with mock objects.
        """
        self.invoice_service = invoice_service
        self.invoice_repository = invoice_repository
        self.storage_repository = storage_repository
        self.pdf_transformer = PDFTransformer()
        self.temp_storage: Optional[TemporaryStorageAdapter] = None

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
            # Check if we have a TemporaryStorageAdapter available
            if not hasattr(self, "temp_storage") or self.temp_storage is None:
                self.temp_storage = TemporaryStorageAdapter(self.storage_repository)
                logger.debug("Created temporary storage adapter")

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
            effective_user_id = user_id or invoice.uploaded_by or 1
            # Validate that effective_user_id exists - in a production system, 
            # we would verify this user exists in the database
            permanent_identifier = f"invoice_{invoice.invoice_number}_{effective_user_id}_{timestamp}"

            logger.debug("Generated permanent identifier: %s", permanent_identifier)

            # Set urgency level if provided
            if urgency_level is not None:
                try:
                    urgency = UrgencyLevel.from_db_value(urgency_level)
                    invoice.set_urgency_manually(urgency)
                    logger.info("Set manual urgency level: %s", urgency.display_name)
                except (ValueError, TypeError) as e:
                    logger.warning("Invalid urgency level value: %s - %s", urgency_level, str(e))
                    # Continue with automatic urgency level

            # Verify temporary file exists before attempting transfer
            try:
                temp_full_path = self.storage_repository.get_file_path(temp_file_path)
                if not temp_full_path.exists():
                    logger.error("Temporary file not found: %s", temp_file_path)
                    raise ProcessingError(f"Temporary file not found: {temp_file_path}")
                logger.debug("Verified temporary file exists: %s", temp_file_path)
            except Exception as e:
                logger.error("Failed to verify temporary file: %s", str(e))
                raise ProcessingError(f"Failed to verify temporary file: {str(e)}") from e

            # Transfer the file to permanent storage
            try:
                logger.info("Transferring file from temporary to permanent storage")
                permanent_path = self.temp_storage.promote_to_permanent(temp_file_path, permanent_identifier)
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
                    "amount": str(saved_invoice.amount) if hasattr(saved_invoice, "amount") else None,
                    "due_date": saved_invoice.due_date.isoformat() if hasattr(saved_invoice, "due_date") else None,
                    "timestamps": {
                        "created_at": getattr(saved_invoice, "created_at", None),
                        "updated_at": getattr(saved_invoice, "updated_at", None),
                    },
                    "buyer": {
                        "name": saved_invoice.buyer.name if hasattr(saved_invoice, "buyer") else None,
                        "address": saved_invoice.buyer.address if hasattr(saved_invoice, "buyer") else None,
                        "email": saved_invoice.buyer.email if hasattr(saved_invoice, "buyer") else None,
                        "vat": saved_invoice.buyer.vat if hasattr(saved_invoice, "buyer") else None,
                    },
                    "seller": {
                        "name": saved_invoice.seller.name if hasattr(saved_invoice, "seller") else None,
                        "vat": saved_invoice.seller.vat if hasattr(saved_invoice, "seller") else None,
                    },
                    "file_metadata": {
                        "size": saved_invoice.file.size if hasattr(saved_invoice, "file") else None,
                        "type": saved_invoice.file.file_type if hasattr(saved_invoice, "file") else None,
                        "original_name": saved_invoice.file.original_name if hasattr(saved_invoice, "file") else None,
                    },
                }

            except StorageError as e:
                logger.error("Storage error during finalization: %s", str(e))
                raise ProcessingError(f"Failed to transfer file to permanent storage: {str(e)}") from e

        except Exception as e:
            logger.error("Invoice finalization failed: %s", str(e), exc_info=True)
            # Include more context about the error type
            error_type = type(e).__name__
            msg = f"Failed to finalize invoice ({error_type}): {str(e)}"
            raise ProcessingError(msg) from e
