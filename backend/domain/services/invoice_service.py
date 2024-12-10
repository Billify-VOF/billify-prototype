"""Service layer for invoice processing business logic.

This service handles the core business operations related to
invoice processing, delegating technical concerns to
appropriate infrastructure components.
"""

from pathlib import Path
from domain.exceptions import (
    ProcessingError,
    InvalidInvoiceError
)
from domain.models.invoice import Invoice
from integrations.transformers.pdf.transformer import (
    PDFTransformer,
    PDFTransformationError
)
from infrastructure.django.repositories.invoice_repository import (
    DjangoInvoiceRepository
)


class InvoiceService:
    """Handles business logic for invoice processing operations."""

    def __init__(self):
        """Initialize service with required components."""
        self.pdf_transformer = PDFTransformer()
        self.invoice_repository = DjangoInvoiceRepository()

    def process_invoice(self, file, storage, user_id: int):
        """
        Process a new invoice file through the complete business workflow.

        Args:
            file: The uploaded invoice file
            storage: Storage implementation for saving the file
            user_id: The ID of the user who uploaded the invoice

        Returns:
            dict: A dictionary containing the ID, invoice number,
                    and status of the processed invoice

        Raises:
            InvalidInvoiceError: If the invoice fails validation
            StorageError: If the file cannot be stored
            ProcessingError: If processing fails
        """
        try:
            # Store the file using the provided storage implementation
            file_path = storage.save_invoice(file)

            # Extract data from the PDF
            invoice_data = self.pdf_transformer.transform(Path(file_path))

            # Create and validate the Invoice object
            invoice = Invoice(**invoice_data)
            invoice.validate()

            # Save to database
            saved_invoice = self.invoice_repository.save(invoice, user_id)

            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status
            }

        except PDFTransformationError as e:
            raise ProcessingError(
                f"Failed to extract data from invoice: {str(e)}"
            ) from e

        except InvalidInvoiceError:
            # Re-raise InvalidInvoiceError as it's already properly typed
            raise

        except Exception as e:
            # For now, we're raising a ProcessingError
            raise ProcessingError(
                f"Failed to process invoice: {str(e)}"
            ) from e
