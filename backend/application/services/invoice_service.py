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
            # Generate unique identifier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            identifier = f"invoice_{user_id}_{timestamp}"

            # Store file and get path
            file_path = self.storage_repository.save_file(file, identifier)
            full_path = self.storage_repository.get_file_path(file_path)

            # Extract file metadata
            file_size = os.path.getsize(full_path)
            file_type = mimetypes.guess_type(full_path)[0] or "unknown"
            original_file_name = file.name

            # Extract invoice metadata
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            logger.info("PDF transformation successful: %s", invoice_data)

            # Extract structured metadata
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

            # Delegate processing to domain service (avoid fetch-edit-save)
            saved_invoice = self.invoice_service.process_invoice(
                invoice_data=invoice_data,
                file_size=file_size,
                file_type=file_type,
                original_file_name=original_file_name,
                file_path=file_path,
                user_id=user_id
            )

            urgency_info = self.invoice_service.get_urgency_info(saved_invoice)

            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status,
                'file_path': file_path,
                'updated': saved_invoice.is_updated,  # Controlled by domain logic
                **invoice_metadata,
                'file_size': file_size,
                'file_type': file_type,
                'original_file_name': original_file_name,
                'urgency': urgency_info
            }

        except PDFTransformationError as e:
            raise ProcessingError(f"PDF_TRANSFORMATION_ERROR: {str(e)}") from e

        except Exception as e:
            try:
                self.storage_repository.delete_file(file_path)
            except StorageError:
                pass
            raise ProcessingError(f"PROCESSING_ERROR: {str(e)}") from e
