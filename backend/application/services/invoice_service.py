"""Application service for invoice processing workflows.

This service orchestrates the overall invoice processing workflow,
coordinating between domain services, repositories and infrastructure
components.
"""

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
    ):
        """Initialize service with required components.

        Args:
            invoice_service: Domain service for invoice business logic
            invoice_repository: Repository for invoice persistence
            storage_repository: Repository for file storage
        """
        self.invoice_service = invoice_service
        self.invoice_repository = invoice_repository
        self.storage_repository = storage_repository
        self.pdf_transformer = PDFTransformer()

    def process_invoice(self, file, user_id: int):
        """Process a new invoice file through the complete workflow.

        This application service method:
        1. Handles file storage
        2. Coordinates PDF transformation
        3. Delegates to domain services for business rules
        4. Manages persistence through repositories

        Args:
            file: The uploaded invoice file
            user_id: The ID of the user who uploaded the invoice

        Returns:
            Dict containing the processed invoice information

        Raises:
            ProcessingError: For failures during processing
            StorageError: For failures storing the file
        """
        try:
            # Generate unique identifier for file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            identifier = f"invoice_{user_id}_{timestamp}"

            # Store file using storage repository
            file_path = self.storage_repository.save_file(file, identifier)

            # Get path for processing
            full_path = self.storage_repository.get_file_path(file_path)

            # Extract data from PDF
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            logger.info("PDF transformation successful: %s", invoice_data)

            # Check for existing invoice
            existing_invoice = self.invoice_repository.get_by_number(
                invoice_data['invoice_number']
            )

            if existing_invoice:
                # Generate old file identifier using invoice number
                old_id = f"invoice_{user_id}_{existing_invoice.invoice_number}"

                # Use domain service to update the invoice with extracted data
                updated_invoice = self.invoice_service.update(
                    existing_invoice,
                    invoice_data
                )

                # Save updated invoice
                saved_invoice = self.invoice_repository.save(
                    updated_invoice,
                    user_id
                )

                # Clean up old file using storage repository
                try:
                    self.storage_repository.delete_file(old_id)
                except StorageError:
                    pass

                # Get urgency information from the domain service
                urgency_info = self.invoice_service.get_urgency_info(updated_invoice)

                return {
                    'invoice_id': saved_invoice.id,
                    'invoice_number': saved_invoice.invoice_number,
                    'status': saved_invoice.status,
                    'file_path': file_path,
                    'updated': True,
                    'amount': updated_invoice.amount,
                    'due_date': updated_invoice.due_date,
                    'supplier_name': invoice_data.get('supplier_name', ''),
                    'urgency': urgency_info
                }

            # Create new invoice using domain service
            new_invoice = self.invoice_service.create(
                invoice_data
            )

            # Persist the invoice
            saved_invoice = self.invoice_repository.save(new_invoice, user_id)

            # Get urgency information from the domain service
            urgency_info = self.invoice_service.get_urgency_info(new_invoice)

            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status,
                'file_path': file_path,
                'updated': False,
                'amount': new_invoice.amount,
                'due_date': new_invoice.due_date,
                'supplier_name': invoice_data.get('supplier_name', ''),
                'urgency': urgency_info
            }

        except PDFTransformationError as e:
            msg = f"Failed to extract data from invoice: {str(e)}"
            # Include error type in message for better handling
            raise ProcessingError(f"PDF_TRANSFORMATION_ERROR: {msg}") from e

        except Exception as e:
            # Clean up stored file on error
            try:
                self.storage_repository.delete_file(file_path)
            except StorageError:
                pass

            # Include more context about the error type
            error_type = type(e).__name__
            msg = f"Failed to process invoice ({error_type}): {str(e)}"
            raise ProcessingError(msg) from e
