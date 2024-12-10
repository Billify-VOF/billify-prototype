"""Django ORM implementation of the invoice repository interface."""

from datetime import date
from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from domain.repositories.interfaces.invoice_repository import InvoiceRepository
from domain.models.invoice import Invoice as DomainInvoice
from infrastructure.django.models.invoice import Invoice as DjangoInvoice


class DjangoInvoiceRepository(InvoiceRepository):
    """Django ORM implementation of the invoice repository."""

    def _to_domain(self, db_invoice: DjangoInvoice) -> DomainInvoice:
        """Convert Django model to domain model."""
        return DomainInvoice(
            amount=db_invoice.amount,
            due_date=db_invoice.due_date,
            invoice_number=db_invoice.invoice_number,
            file_path=db_invoice.file_path,
            invoice_id=db_invoice.id
        )

    def _to_django(
        self,
        domain_invoice: DomainInvoice,
        user_id: int
    ) -> DjangoInvoice:
        """Convert domain model to Django model."""
        return DjangoInvoice(
            invoice_number=domain_invoice.invoice_number,
            amount=domain_invoice.amount,
            due_date=domain_invoice.due_date,
            file_path=domain_invoice.file_path,
            status=domain_invoice.status,
            uploaded_by_id=user_id
        )

    def save(self, invoice: DomainInvoice, user_id: int) -> DomainInvoice:
        """Save an invoice to the database."""
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
        """Retrieve an invoice by its number."""
        try:
            db_invoice = DjangoInvoice.objects.get(
                invoice_number=invoice_number
            )
            return self._to_domain(db_invoice)
        except ObjectDoesNotExist:
            return None

    def list_by_status(self, status: str) -> List[DomainInvoice]:
        """List all invoices with a given status."""
        db_invoices = DjangoInvoice.objects.filter(status=status)
        return [self._to_domain(invoice) for invoice in db_invoices]

    def list_overdue(self, as_of: date = None) -> List[DomainInvoice]:
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
