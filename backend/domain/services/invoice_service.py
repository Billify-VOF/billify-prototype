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


class InvoiceService:
    """Handles business logic for invoice processing operations."""

    def __init__(self):
        """Initialize service with required components."""
        self.pdf_transformer = PDFTransformer()

    def process_invoice(self, file, storage):
        """
        Process a new invoice file through the complete business workflow.

        Args:
            file: The uploaded invoice file
            storage: Storage implementation for saving the file
            user: The user who uploaded the invoice

        Returns:
            Invoice: The processed invoice object

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

            # Create an Invoice object
            invoice = Invoice(**invoice_data)

            # Validate the invoice according to business rules
            invoice.validate()

            # Here we would typically:
            # 3. Create invoice records
            # 4. Update any related business data
            # In a full implementation, we would persist
            # the structured data to our database here

            # For now, return a simple structure
            return invoice

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
