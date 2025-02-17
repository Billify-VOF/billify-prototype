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
from domain.repositories.interfaces.invoice_repository import InvoiceRepository
from domain.repositories.interfaces.storage_repository import StorageRepository
from datetime import datetime  # We'll need this for generating identifiers


class InvoiceService:
    """Handles business logic for invoice processing operations."""

    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        storage_repository: StorageRepository
    ):
        """Initialize service with required components."""
        self.pdf_transformer = PDFTransformer()
        self.invoice_repository = invoice_repository
        self.storage_repository = storage_repository

    def process_invoice(self, file, user_id: int):
        """Process a new invoice file through the complete business workflow.

        Args:
            file: The uploaded invoice file
            user_id: The ID of the user who uploaded the invoice
        """
        try:
            # Generate unique identifier for file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            identifier = f"invoice_{user_id}_{timestamp}"

            # Store file using new interface
            file_path = self.storage_repository.save_file(file, identifier)

            # Get path for processing
            full_path = self.storage_repository.get_file_path(file_path)

            # Extract data from PDF
            invoice_data = self.pdf_transformer.transform(Path(full_path))
            print(f"PDF transformation successful: {invoice_data}")

            # Check for existing invoice
            existing_invoice = self.invoice_repository.get_by_number(
                invoice_data['invoice_number']
            )

            if existing_invoice:
                # Generate old file identifier using invoice number
                old_id = f"invoice_{user_id}_{existing_invoice.invoice_number}"

                # Update invoice data (without file_path)
                existing_invoice.amount = invoice_data['amount']
                existing_invoice.due_date = invoice_data['due_date']
                existing_invoice.validate()

                # Save updated invoice
                saved_invoice = self.invoice_repository.save(
                    existing_invoice, 
                    user_id
                )

                # Clean up old file using storage repository
                try:
                    self.storage_repository.delete_file(old_id)
                except StorageError:
                    pass

                return {
                    'invoice_id': saved_invoice.id,
                    'invoice_number': saved_invoice.invoice_number,
                    'status': saved_invoice.status,
                    'file_path': file_path,  # Keep in response
                    'updated': True
                }

            # Create new invoice
            print(f"Invoice data before creation: {invoice_data}")
            print("Creating invoice with:")
            amount_type = type(invoice_data['amount'])
            print(f"  amount: {invoice_data['amount']} ({amount_type})")
            due_date_type = type(invoice_data['due_date'])
            print(f"  due_date: {invoice_data['due_date']} ({due_date_type})")
            number_type = type(invoice_data['invoice_number'])
            print(
                f"  invoice_number: {invoice_data['invoice_number']} "
                f"({number_type})"
            )
            invoice_data.pop('file_path', None)  # Remove file_path from data
            print(f"Invoice data after pop (full dict): {invoice_data}")

            module_name = f"{Invoice.__module__}.{Invoice.__name__}"
            print(f"Invoice class being used: {module_name}")

            invoice = Invoice(
                amount=invoice_data['amount'],
                due_date=invoice_data['due_date'],
                invoice_number=invoice_data['invoice_number']
            )
            invoice.validate()
            saved_invoice = self.invoice_repository.save(invoice, user_id)

            return {
                'invoice_id': saved_invoice.id,
                'invoice_number': saved_invoice.invoice_number,
                'status': saved_invoice.status,
                'file_path': file_path,  # Keep in response
                'updated': False
            }

        except PDFTransformationError as e:
            msg = f"Failed to extract data from invoice: {str(e)}"
            raise ProcessingError(msg) from e
        except Exception as e:
            # Clean up stored file on error
            try:
                self.storage_repository.delete_file(file_path)
            except StorageError:
                pass
            msg = f"Failed to process invoice: {str(e)}"
            raise ProcessingError(msg) from e
