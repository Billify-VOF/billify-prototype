"""This module contains the domain service for invoices. It encapsulates business
logic related to invoices, ensures adherence to domain rules, and enforces
invariants for invoice operations. It contains no references to infrastructure
or application-specific concerns.

This service contains pure domain logic related to invoices,
independent of infrastructure concerns like storage or data transformation.

NOTE: Currently this service mixes some domain, infrastructure, and application 
layer concerns. This is a known technical debt that should be refactored 
post-MVP to better adhere to clean architecture principles. The current 
implementation was kept due to time constraints for the MVP release.
"""

from typing import Dict, Any, List, Optional
from domain.models.invoice import Invoice
from domain.models.value_objects import InvoiceStatus


class InvoiceService:
    """Domain service that implements business logic for invoice operations."""

    def update(self, invoice: Invoice, extracted_data: Dict[str, Any]) -> Invoice:
        """Update an invoice with data extracted from a document.

        This method applies business rules for updating an existing invoice
        with extracted data, ensuring the domain model remains valid.

        Args:
            invoice: The invoice to update
            extracted_data: Data dictionary with extracted invoice information

        Returns:
            The updated invoice

        Raises:
            ValueError: If the extracted data is invalid
        """
        # Delegate to the domain model's update method
        invoice.update(
            amount=extracted_data["amount"],
            due_date=extracted_data["due_date"],
        )

        return invoice

    def create(self, extracted_data: Dict[str, Any]) -> Invoice:
        """Create a new invoice from extracted document data.

        This method applies business rules for creating a new invoice
        from extracted data, ensuring all required fields are present
        and valid.

        Args:
            extracted_data: Data dictionary with extracted invoice information

        Returns:
            A new Invoice instance

        Raises:
            ValueError: If the extracted data is missing required fields
        """
        # Remove any non-domain fields
        extracted_data.pop("file_path", None)

        # Use the factory method to create and validate the invoice
        return Invoice.create(
            amount=extracted_data["amount"],
            due_date=extracted_data["due_date"],
            invoice_number=extracted_data["invoice_number"],
        )

    def update_statuses(self, invoices: List[Invoice]) -> None:
        """Recalculate status for a collection of invoices.

        This is a batch operation that can be used to update the status of
        multiple invoices based on current date and business rules.

        Args:
            invoices: List of invoices to update
        """
        for invoice in invoices:
            # Using the domain model's built-in methods to update status
            if invoice.status == InvoiceStatus.PENDING and invoice.is_overdue():
                invoice.mark_as_overdue()

    def _calculate_status(self, invoice: Invoice, current_date) -> InvoiceStatus:
        """Determine the status of an invoice based on business rules.

        Args:
            invoice: The invoice to evaluate
            current_date: The current date to compare against

        Returns:
            The calculated InvoiceStatus enum value
        """
        # This method is now private to the service and can be used
        # for more complex status determination logic in the future
        if invoice.is_paid:
            return InvoiceStatus.PAID
        elif invoice.due_date < current_date:
            return InvoiceStatus.OVERDUE
        else:
            return InvoiceStatus.PENDING

    def get_urgency_info(self, invoice: Invoice) -> Dict[str, Any]:
        """Extract urgency information from an invoice in a format suitable for APIs.

        This method transforms the UrgencyLevel enum to a dictionary containing
        all relevant information for presentation purposes.

        Args:
            invoice: The invoice to extract urgency information from

        Returns:
            Dict with urgency level, display name, color code, and manual flag
        """
        # Get the UrgencyLevel enum from the invoice
        urgency_level = invoice.urgency

        # Check if urgency was manually set
        is_manually_set = invoice.is_urgency_manually_set()

        # Return a dictionary with all relevant information
        return {
            "level": urgency_level.name if urgency_level else None,
            "display_name": urgency_level.display_name if urgency_level else None,
            "color_code": urgency_level.color_code if urgency_level else None,
            "is_manual": is_manually_set,
        }

    def _find_existing_invoice(self, invoice_number: str) -> Optional[Invoice]:
        """Find an existing invoice by number using repository.

        This method abstracts the repository lookup to maintain separation of concerns
        and single responsibility principle.

        Args:
            invoice_number: The business identifier of the invoice to find

        Returns:
            The existing invoice if found, None otherwise
        """
        if hasattr(self, "invoice_repository") and self.invoice_repository:
            return self.invoice_repository.find_by_invoice_number(invoice_number)
        return None

    def _update_file_metadata(
        self,
        invoice: Invoice,
        file_path: Optional[str],
        file_size: Optional[int],
        file_type: Optional[str],
        original_file_name: Optional[str],
    ) -> None:
        """Update invoice with file-related metadata.

        This method handles the attachment of file metadata to the invoice model,
        adapting to the structure of the invoice object.

        Args:
            invoice: The invoice to update
            file_path: Path where the file is stored
            file_size: Size of the file in bytes
            file_type: MIME type of the file
            original_file_name: Original name of the uploaded file
        """
        if hasattr(invoice, "file"):
            if file_path:
                invoice.file.path = file_path
            if file_size:
                invoice.file.size = file_size
            if file_type:
                invoice.file.type = file_type
            if original_file_name:
                invoice.file.original_name = original_file_name
        elif hasattr(invoice, "file_path") and file_path:
            invoice.file_path = file_path

    def process_invoice(
        self,
        invoice_data: Dict[str, Any],
        file_size: Optional[int] = None,
        file_type: Optional[str] = None,
        original_file_name: Optional[str] = None,
        file_path: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Invoice:
        """Process an invoice, creating a new one or updating existing.

        This method consolidates the create and update logic into a single method
        that handles both new and existing invoices based on the invoice number.

        Args:
            invoice_data: Dictionary with extracted invoice information (amount, due_date, etc.)
            file_size: Size of the uploaded file in bytes
            file_type: MIME type of the file
            original_file_name: Original name of the uploaded file
            file_path: Path where the file is stored
            user_id: ID of the user who uploaded the invoice

        Returns:
            Processed Invoice instance (either created or updated)

        Raises:
            ValueError: If the invoice data is missing required fields
        """
        # Validate required data
        invoice_number = invoice_data.get("invoice_number")
        if not invoice_number:
            raise ValueError("Missing required field: invoice_number")

        # Find existing invoice
        existing_invoice = self._find_existing_invoice(invoice_number)

        # Process invoice based on whether it exists
        if existing_invoice:
            invoice = self.update(existing_invoice, invoice_data)
            setattr(invoice, "is_updated", True)
        else:
            invoice = self.create(invoice_data)
            setattr(invoice, "is_updated", False)

        # Update file metadata
        self._update_file_metadata(
            invoice,
            file_path,
            file_size,
            file_type,
            original_file_name,
        )

        # Set user if not already set
        if hasattr(invoice, "uploaded_by") and user_id and not invoice.uploaded_by:
            invoice.uploaded_by = user_id

        # Save if repository available
        if hasattr(self, "invoice_repository") and self.invoice_repository:
            return self.invoice_repository.save(invoice, user_id)

        return invoice
