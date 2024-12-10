"""Invoice repository interface for data access operations."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from domain.models.invoice import Invoice


class InvoiceRepository(ABC):
    """Interface defining invoice data access operations."""

    @abstractmethod
    def save(self, invoice: Invoice, user_id: int) -> Invoice:
        """
        Save an invoice to the database.

        Args:
            invoice: The domain invoice to save
            user_id: ID of the user who uploaded the invoice
        """

    @abstractmethod
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Retrieve an invoice by its ID."""

    @abstractmethod
    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Retrieve an invoice by its number."""

    @abstractmethod
    def list_by_status(self, status: str) -> List[Invoice]:
        """List all invoices with a given status."""

    @abstractmethod
    def list_overdue(self, as_of: date = None) -> List[Invoice]:
        """List all overdue invoices."""

    @abstractmethod
    def update_status(self, invoice_id: int, status: str) -> bool:
        """Update the status of an invoice."""
