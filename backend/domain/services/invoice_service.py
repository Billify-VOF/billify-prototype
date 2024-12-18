"""Service layer for invoice processing business logic.

This service handles the core business operations related to
invoice processing, delegating technical concerns to
appropriate infrastructure components.
"""

from pathlib import Path
from domain.exceptions import ProcessingError, StorageError
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
            print(f"Processing invoice file: {file.name}")
            print(f"Processing invoice for user_id: {user_id}")

            # Store the file using the provided storage implementation
            file_path = storage.save_invoice(file)
            print(f"File saved with relative path: {file_path}")

            full_path = storage.get_file_path(file_path)
            print(f"Full path: {full_path}")

            # Extract data from the PDF
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            print(f"PDF transformation successful: {invoice_data}")

            # Check for existing invoice with same number
            existing_invoice = self.invoice_repository.get_by_number(
                invoice_data['invoice_number']
            )

            # Update existing invoice if found
            if existing_invoice:
                # Store old file path for cleanup
                old_file_path = existing_invoice.file_path

                # Update invoice with new data
                existing_invoice.amount = invoice_data['amount']
                existing_invoice.due_date = invoice_data['due_date']
                existing_invoice.file_path = file_path
                existing_invoice.validate()

                # Save updated invoice
                saved_invoice = self.invoice_repository.update(
                    existing_invoice, 
                    user_id
                )

                # Clean up old file
                try:
                    storage.delete_file(old_file_path)
                except StorageError:
                    # Log but continue if old file cleanup fails
                    pass

                return {
                    'invoice_id': saved_invoice.id,
                    'invoice_number': saved_invoice.invoice_number,
                    'status': saved_invoice.status,
                    'file_path': file_path,
                    'updated': True
                }

            # Create new invoice if no existing one found
            invoice = Invoice(**invoice_data)
            invoice.validate()
            saved_invoice = self.invoice_repository.save(invoice, user_id)

            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status,
                'file_path': file_path,
                'updated': False
            }

        except PDFTransformationError as e:
            raise ProcessingError(
                f"Failed to extract data from invoice: {str(e)}"
            ) from e
        except Exception as e:
            # Clean up stored file on any error
            try:
                storage.delete_file(file_path)
            except StorageError:
                pass  # Log but continue if cleanup fails
            raise ProcessingError(
                f"Failed to process invoice: {str(e)}"
            ) from e
