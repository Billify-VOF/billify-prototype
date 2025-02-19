"""Django ORM implementation of the invoice repository interface."""

from datetime import date
from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from domain.repositories.interfaces.invoice_repository import InvoiceRepository
from domain.models.invoice import Invoice as DomainInvoice
from domain.exceptions import InvalidInvoiceError
from infrastructure.django.models.invoice import Invoice as DjangoInvoice
from domain.models.value_objects import UrgencyLevel, InvoiceStatus


class DjangoInvoiceRepository(InvoiceRepository):
    """Django ORM implementation of the invoice repository."""

    def _to_domain(self, db_invoice: DjangoInvoice) -> DomainInvoice:
        """Convert Django model to domain model.

        This method is used:
        1. When fetching data from the database
        2. Before returning data to business logic layer

        What it does:
        1. Takes database fields and maps them to domain model attributes
        2. Preserves the database ID for future reference
        3. Ensures data is in the format our domain logic expects

        Note:
            The `id` field is automatically provided by Django's ORM.
            Every Django model gets an auto-incrementing integer primary key
            field named 'id' unless explicitly specified otherwise.

        Args:
            db_invoice: Django ORM invoice model instance

        Returns:
            DomainInvoice: Domain model populated with database values

        Example:
            # When fetching by ID:
            db_invoice = DjangoInvoice.objects.get(id=123)
            domain_invoice = self._to_domain(db_invoice)
            return domain_invoice  # Ready for business logic
        """
        print(f"Converting DB invoice to domain model: {db_invoice}")
        invoice_args = {
            'amount': db_invoice.amount,
            'due_date': db_invoice.due_date,
            'invoice_number': db_invoice.invoice_number,
            # Map Django's auto-generated id to domain model's
            # invoice_id parameter. Domain model stores it as self.id
            'invoice_id': db_invoice.id,
            'status': InvoiceStatus.from_db_value(db_invoice.status)
        }
        print(f"Created invoice args: {invoice_args}")

        if db_invoice.manual_urgency is not None:
            invoice_args['_manual_urgency'] = (
                UrgencyLevel.from_db_value(db_invoice.manual_urgency)
            )

        return DomainInvoice(**invoice_args)

    def _to_django(
        self,
        domain_invoice: DomainInvoice,
        user_id: int,
        file_path: Optional[str] = None
    ) -> DjangoInvoice:
        """Convert domain model to Django model.

        This method is used:
        1. When saving new invoices to database
        2. When updating existing invoices

        What it does:
        1. Takes domain model attributes and maps them to database fields
        2. Adds necessary database-specific information (like user_id)
        3. Prepares data for database storage

        Args:
            domain_invoice: Domain model instance to convert
            user_id: ID of the user who uploaded/created the invoice
            file_path: Optional path to stored file. If not provided, will be
                updated later.

        Returns:
            DjangoInvoice: Django ORM model ready for database operations

        Example:
            # When saving a new invoice:
            db_invoice = self._to_django(domain_invoice, user_id)
            db_invoice.save()
            return self._to_domain(db_invoice)  # Convert back after saving
        """
        # Get the db_value from the manual urgency if it exists
        manual_urgency_value = (
            domain_invoice._manual_urgency.db_value
            if domain_invoice._manual_urgency is not None
            else None
        )

        return DjangoInvoice(
            invoice_number=domain_invoice.invoice_number,
            amount=domain_invoice.amount,
            due_date=domain_invoice.due_date,
            file_path=file_path or '',
            status=domain_invoice.status.value,
            manual_urgency=manual_urgency_value,
            uploaded_by_id=user_id
        )

    def save(self, invoice: DomainInvoice, user_id: int) -> DomainInvoice:
        """Save an invoice to the database."""
        # come back to this later
        db_invoice = self._to_django(invoice, user_id)
        db_invoice.save()
        return self._to_domain(db_invoice)

    def get_by_id(self, invoice_id: int) -> Optional[DomainInvoice]:
        """Retrieve an invoice by its ID."""
        try:
            db_invoice = DjangoInvoice.objects.get(id=invoice_id)
            return self._to_domain(db_invoice)
        except ObjectDoesNotExist:
            return None

    def get_by_number(self, invoice_number: str) -> Optional[DomainInvoice]:
        """Retrieve an invoice by its number.

        If multiple invoices exist with the same number (due to OCR errors,
        different suppliers, etc.), returns the most recently created one.
        """
        print(f"Searching for invoice with number: {invoice_number}")
        print(f"Type of invoice_number: {type(invoice_number)}")
        try:
            # Order by created_at descending and get the first one
            db_invoice = DjangoInvoice.objects.filter(
                invoice_number=invoice_number
            ).order_by('-created_at').first()

            if db_invoice:
                print(f"Found invoice in DB: {db_invoice}")
                return self._to_domain(db_invoice)
            else:
                print("No invoice found with that number")
                return None

        except Exception as e:
            print(f"Error retrieving invoice: {str(e)}")
            return None

    def list_by_status(self, status: str) -> List[DomainInvoice]:
        """List all invoices with a given status."""
        db_invoices = DjangoInvoice.objects.filter(status=status)
        return [self._to_domain(invoice) for invoice in db_invoices]

    def list_overdue(self, as_of: Optional[date] = None) -> List[DomainInvoice]:
        """List all overdue invoices."""
        check_date = as_of or date.today()
        db_invoices = DjangoInvoice.objects.filter(
            Q(due_date__lt=check_date) & Q(status='pending')
        )
        return [self._to_domain(invoice) for invoice in db_invoices]

    def update_status(self, invoice_id: int, status: str) -> bool:
        """Update the status of an invoice."""
        try:
            invoice = DjangoInvoice.objects.get(id=invoice_id)
            invoice.status = status
            invoice.save()
            return True
        except ObjectDoesNotExist:
            return False

    def update(self, invoice: DomainInvoice, user_id: int) -> DomainInvoice:
        """Update an existing invoice.

        Args:
            invoice: Domain invoice with updated data
            user_id: ID of the user performing the update

        Returns:
            DomainInvoice: Updated domain invoice

        Raises:
            InvalidInvoiceError: If invoice doesn't exist
        """
        try:
            db_invoice = DjangoInvoice.objects.get(
                invoice_number=invoice.invoice_number
            )
            # Update fields from domain model
            db_invoice.amount = invoice.amount
            db_invoice.due_date = invoice.due_date
            db_invoice.status = invoice.status
            # Update the user who modified it
            db_invoice.uploaded_by_id = user_id
            db_invoice.save()
            return self._to_domain(db_invoice)
        except ObjectDoesNotExist as exc:
            raise InvalidInvoiceError(
                f"Invoice {invoice.invoice_number} not found"
            ) from exc
