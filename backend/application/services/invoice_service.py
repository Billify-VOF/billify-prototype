import os
import mimetypes
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
    """Application service that orchestrates invoice processing workflows."""

    def __init__(
        self,
        invoice_service: InvoiceService,
        invoice_repository: InvoiceRepository,
        storage_repository: StorageRepository
    ):
        """Initialize service with required components."""
        self.invoice_service = invoice_service
        self.invoice_repository = invoice_repository
        self.storage_repository = storage_repository
        self.pdf_transformer = PDFTransformer()

    def process_invoice(self, file, user_id: int):
        """Process a new invoice file through the complete workflow."""
        try:
            # Generate unique file identifier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            identifier = f"invoice_{user_id}_{timestamp}"

            # Store file and get file path
            file_path = self.storage_repository.save_file(file, identifier)
            full_path = self.storage_repository.get_file_path(file_path)

            # **NEW:** Extract file metadata
            file_size = os.path.getsize(full_path)  # File size in bytes
            file_type = mimetypes.guess_type(full_path)[0] or "unknown"  # MIME type
            original_file_name = file.name  # Original filename from upload

            # Extract invoice metadata from PDF
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            logger.info("PDF transformation successful: %s", invoice_data)

            # Extract other invoice metadata
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

            # Check if invoice already exists
            existing_invoice = self.invoice_repository.get_by_number(invoice_data['invoice_number'])

            if existing_invoice:
                # Update existing invoice
                updated_invoice = self.invoice_service.update(
                    existing_invoice,
                    invoice_data,
                    file_size=file_size,
                    file_type=file_type,
                    original_file_name=original_file_name,
                    **invoice_metadata  # Pass all extracted metadata
                )

                saved_invoice = self.invoice_repository.save(updated_invoice, user_id)

                # Get urgency information from domain service
                urgency_info = self.invoice_service.get_urgency_info(updated_invoice)

                return {
                    'invoice_id': saved_invoice.id,
                    'invoice_number': saved_invoice.invoice_number,
                    'status': saved_invoice.status,
                    'file_path': file_path,
                    'updated': True,
                    **invoice_metadata,  # Include metadata in response
                    'file_size': file_size,
                    'file_type': file_type,
                    'original_file_name': original_file_name,
                    'urgency': urgency_info
                }

            # Create new invoice with metadata
            new_invoice = self.invoice_service.create(
                invoice_data,
                file_size=file_size,
                file_type=file_type,
                original_file_name=original_file_name,
                **invoice_metadata  # Pass all metadata
            )

            # Persist the invoice
            saved_invoice = self.invoice_repository.save(new_invoice, user_id)

            # Get urgency information from domain service
            urgency_info = self.invoice_service.get_urgency_info(new_invoice)

            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status,
                'file_path': file_path,
                'updated': False,
                **invoice_metadata,  # Include metadata in response
                'file_size': file_size,
                'file_type': file_type,
                'original_file_name': original_file_name,
                'urgency': urgency_info
            }

        except PDFTransformationError as e:
            msg = f"Failed to extract data from invoice: {str(e)}"
            raise ProcessingError(f"PDF_TRANSFORMATION_ERROR: {msg}") from e

        except Exception as e:
            try:
                self.storage_repository.delete_file(file_path)
            except StorageError:
                pass

            error_type = type(e).__name__
            msg = f"Failed to process invoice ({error_type}): {str(e)}"
            raise ProcessingError(msg) from e
