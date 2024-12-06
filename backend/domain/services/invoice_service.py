"""Service layer for invoice processing business logic.

This service handles the core business operations related to
invoice processing, delegating technical concerns to
appropriate infrastructure components.
"""

from domain.exceptions import (
    ProcessingError,
)


class InvoiceService:
    """Handles business logic for invoice processing operations."""

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

            # Here we would typically:
            # 1. Extract data from the PDF
            # 2. Validate the extracted data
            # 3. Create invoice records
            # 4. Update any related business data

            # For now, return a simple structure
            return {
                'id': '12345',  # This would be a real ID in production
                'status': 'processed',
                'file_path': file_path
            }

        except Exception as e:
            # For now, we're raising a ProcessingError
            raise ProcessingError(
                f"Failed to process invoice: {str(e)}"
            ) from e
