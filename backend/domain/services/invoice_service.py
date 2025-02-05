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

    def __init__(self, invoice_repository: InvoiceRepository, storage_repository: StorageRepository):
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
            identifier = f"invoice_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
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
                old_identifier = f"invoice_{user_id}_{existing_invoice.invoice_number}"
                
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
                    self.storage_repository.delete_file(old_identifier)
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
            print(f"Creating invoice with:")
            print(f"  amount: {invoice_data['amount']} ({type(invoice_data['amount'])})")
            print(f"  due_date: {invoice_data['due_date']} ({type(invoice_data['due_date'])})")
            print(f"  invoice_number: {invoice_data['invoice_number']} ({type(invoice_data['invoice_number'])})")
            invoice_data.pop('file_path', None)  # Remove file_path from data
            print(f"Invoice data after pop (full dict): {invoice_data}")

            print(f"Invoice class being used: {Invoice.__module__}.{Invoice.__name__}")

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
            raise ProcessingError(f"Failed to extract data from invoice: {str(e)}") from e
        except Exception as e:
            # Clean up stored file on error
            try:
                self.storage_repository.delete_file(file_path)
            except StorageError:
                pass
            raise ProcessingError(f"Failed to process invoice: {str(e)}") from e
