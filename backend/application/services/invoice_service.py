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
    PDFTransformationError
)
from logging import getLogger
from typing import BinaryIO, Dict, Any

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
        storage_repository: StorageRepository
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

    def process_invoice(self, file: BinaryIO, user_id: int) -> dict:
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
            # Generate unique identifier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            identifier = f"invoice_{user_id}_{timestamp}"
            logger.debug("Generated identifier: %s", identifier)

            # Store file and get path
            logger.info("Saving invoice file to storage")
            file_path = self.storage_repository.save_file(file, identifier)
            full_path = self.storage_repository.get_file_path(file_path)
            logger.debug("File saved at path: %s", full_path)

            # Extract file metadata
            logger.info("Extracting file metadata")
            file_size = os.path.getsize(full_path)
            file_type = mimetypes.guess_type(full_path)[0] or "unknown"
            original_file_name = file.name
            logger.debug("File metadata: size=%s bytes, type=%s, name=%s", 
                         file_size, file_type, original_file_name)

            # Extract invoice metadata
            logger.info("Starting PDF transformation to extract invoice data")
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            if invoice_data.get('invoice_number'):
                logger.info("PDF transformation successful for invoice number: %s", 
                            invoice_data.get('invoice_number'))
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
            logger.debug("Structured metadata extracted: %s", 
                        {k: v for k, v in invoice_metadata.items() if v is not None})

            # Delegate processing to domain service (avoid fetch-edit-save)
            logger.info("Delegating to domain service for invoice processing")
            saved_invoice = self.invoice_service.process_invoice(
                invoice_data=invoice_data,
                file_size=file_size,
                file_type=file_type,
                original_file_name=original_file_name,
                file_path=file_path,
                user_id=user_id
            )
            logger.info("Invoice successfully processed and saved with ID: %s", saved_invoice.id)

            logger.info("Retrieving urgency information")
            urgency_info = self.invoice_service.get_urgency_info(saved_invoice)
            logger.debug("Urgency information: %s", urgency_info)

            # Invoice processing completed successfully
            updated = getattr(saved_invoice, 'is_updated', False)
            logger.info("Invoice processing completed successfully")
            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status,
                'file_path': file_path,
                'updated': updated,  # Use getattr to handle missing attribute
                **invoice_metadata,
                'file_size': file_size,
                'file_type': file_type,
                'original_file_name': original_file_name,
                'urgency': urgency_info
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
                
            raise ProcessingError(f"PROCESSING_ERROR: {str(e)}") from e
