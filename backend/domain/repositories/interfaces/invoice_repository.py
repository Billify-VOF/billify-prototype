"""Invoice repository interface for data access operations.

This module defines the abstract interface for invoice data access operations
using Python's ABC (Abstract Base Class). The interface serves as a contract
that all concrete repository implementations must follow.

Key concepts:
    - ABC (Abstract Base Class): Defines an interface that cannot be
      instantiated directly
    - @abstractmethod: Marks methods that MUST be implemented by any
      concrete repository class
    - Repository Pattern: Separates domain logic from data access
      implementation details

Example:
    # Concrete implementation must implement all abstract methods
    class PostgresInvoiceRepository(InvoiceRepository):
        def save(self, invoice: Invoice, user_id: int) -> Invoice:
            # Implementation specific to PostgreSQL
            pass
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from domain.models.invoice import Invoice


class InvoiceRepository(ABC):
    """Interface defining invoice data access operations.

    This abstract base class serves as a contract for invoice persistence
    operations. Any concrete implementation (e.g., Django ORM, SQLAlchemy,
    etc.) must implement all methods marked with @abstractmethod.

    The Repository pattern used here:
    1. Separates domain logic from data access details
    2. Makes the system more maintainable and testable
    3. Allows swapping different storage implementations without changing
       domain code
    4. Follows the Dependency Inversion Principle (SOLID)

    Example:
        class DjangoInvoiceRepository(InvoiceRepository):
            def save(self, invoice: Invoice, user_id: int) -> Invoice:
                # Django ORM specific implementation
                pass
    """

    @abstractmethod
    def save(self, invoice: Invoice, user_id: int) -> Invoice:
        """Save an invoice to the database.

        This method must either create a new invoice or update an existing one
        based on the invoice number. It should handle the persistence details
        while maintaining the domain model's integrity.

        Args:
            invoice (Invoice): The domain invoice model to persist
            user_id (int): ID of the user who uploaded/created the invoice

        Returns:
            Invoice: The persisted domain invoice model, potentially with
                    updated metadata (e.g., ID, timestamps)

        Raises:
            InvalidInvoiceError: If the invoice data is invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Retrieve an invoice by its ID.

        Args:
            invoice_id (int): The unique identifier of the invoice

        Returns:
            Optional[Invoice]: The domain invoice model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Retrieve an invoice by its number.

        Args:
            invoice_number (str): The business-specific invoice number

        Returns:
            Optional[Invoice]: The domain invoice model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def list_by_status(self, status: str) -> List[Invoice]:
        """List all invoices with a given status.

        Args:
            status (str): The invoice status to filter by (e.g., 'pending',
                         'paid')

        Returns:
            List[Invoice]: List of domain invoice models matching the status

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def list_overdue(self, as_of: Optional[date] = None) -> List[Invoice]:
        """List all overdue invoices.

        Retrieves invoices that are past their due date and still pending.
        If no date is provided, uses the current date for comparison.

        Args:
            as_of (date, optional): The date to check against. Defaults to
                                  today.

        Returns:
            List[Invoice]: List of overdue domain invoice models

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def update_status(self, invoice_id: int, status: str) -> bool:
        """Update the status of an invoice.

        Args:
            invoice_id (int): The unique identifier of the invoice
            status (str): The new status value

        Returns:
            bool: True if the update was successful, False if invoice not found

        Raises:
            InvalidStatusError: If the status value is invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def update(self, invoice: Invoice, user_id: int) -> Invoice:
        """Update an existing invoice.

        This method should update all fields of an existing invoice while
        maintaining any metadata (e.g., created_at timestamp).

        Args:
            invoice (Invoice): The domain invoice with updated data
            user_id (int): ID of the user performing the update

        Returns:
            Invoice: The updated domain invoice model

        Raises:
            InvalidInvoiceError: If the invoice doesn't exist or data is
                               invalid
            RepositoryError: If there's a persistence-related error
        """
