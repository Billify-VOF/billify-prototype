"""Domain service for invoice business logic.

This service contains pure domain logic related to invoices,
independent of infrastructure concerns like storage or data transformation.
"""

from typing import Dict, Any, List
from domain.models.invoice import Invoice
from domain.models.value_objects import InvoiceStatus


class InvoiceService:
    """Domain service that implements business logic for invoice operations."""

    def update(
        self,
        invoice: Invoice,
        extracted_data: Dict[str, Any]
    ) -> Invoice:
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
            amount=extracted_data['amount'],
            due_date=extracted_data['due_date']
        )

        return invoice

    def create(
        self,
        extracted_data: Dict[str, Any]
    ) -> Invoice:
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
        extracted_data.pop('file_path', None)

        # Use the factory method to create and validate the invoice
        return Invoice.create(
            amount=extracted_data['amount'],
            due_date=extracted_data['due_date'],
            invoice_number=extracted_data['invoice_number']
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
            if invoice.status == InvoiceStatus.PENDING:
                if invoice.is_overdue():
                    invoice.mark_as_overdue()

    def _calculate_status(
        self,
        invoice: Invoice,
        current_date
    ) -> InvoiceStatus:
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
            'level': urgency_level.name if urgency_level else None,
            'display_name': urgency_level.name.title().replace('_', ' ') if urgency_level else None,
            'color_code': getattr(urgency_level, 'color_code', None),
            'is_manual': is_manually_set
        }
