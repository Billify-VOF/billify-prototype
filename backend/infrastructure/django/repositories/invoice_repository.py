"""Django ORM implementation of the invoice repository interface."""

from datetime import date, timedelta
from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from domain.repositories.interfaces.invoice_repository import InvoiceRepository
from domain.models.invoice import Invoice as DomainInvoice
from domain.exceptions import InvalidInvoiceError
from infrastructure.django.models.invoice import Invoice as DjangoInvoice
from domain.models.value_objects import UrgencyLevel, InvoiceStatus
from logging import getLogger
from django.db import models
from itertools import chain


# Module-level logger
logger = getLogger(__name__)


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
        logger.debug("Converting DB invoice to domain model: %s", db_invoice)
        # All Django models have an id field by default
        invoice_args = {
            'amount': db_invoice.amount,
            'due_date': db_invoice.due_date,
            'invoice_number': db_invoice.invoice_number,
            # Map Django's auto-generated id to domain model's
            # invoice_id parameter. Domain model stores it as self.id
            'invoice_id': db_invoice.id,  # type: ignore[attr-defined]
            'status': InvoiceStatus.from_db_value(db_invoice.status),
            'uploaded_by': db_invoice.uploaded_by_id,
            'file_path': db_invoice.file_path,
            'buyer_name': db_invoice.buyer_name,
            'buyer_address': db_invoice.buyer_address,
            'buyer_email': db_invoice.buyer_email,
            'buyer_vat': db_invoice.buyer_vat,
            'seller_name': db_invoice.seller_name,
            'seller_vat': db_invoice.seller_vat,
            'payment_method': db_invoice.payment_method,
            'currency': db_invoice.currency,
            'iban': db_invoice.iban,
            'bic': db_invoice.bic,
            'payment_processor': db_invoice.payment_processor,
            'transaction_id': db_invoice.transaction_id,
            'subtotal': db_invoice.subtotal,
            'vat_amount': db_invoice.vat_amount,
            'total_amount': db_invoice.total_amount,
            
        }
        logger.debug("Created invoice args: %s", invoice_args)

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
            uploaded_by_id=user_id,
            buyer_name=domain_invoice.buyer_name,
            buyer_address=domain_invoice.buyer_address,
            buyer_email=domain_invoice.buyer_email,
            buyer_vat=domain_invoice.buyer_vat,
            seller_name=domain_invoice.seller_name,
            seller_vat=domain_invoice.seller_vat,
            payment_method=domain_invoice.payment_method,
            currency=domain_invoice.currency,
            iban=domain_invoice.iban,
            bic=domain_invoice.bic,
            payment_processor=domain_invoice.payment_processor,
            transaction_id=domain_invoice.transaction_id,
            subtotal=domain_invoice.subtotal,
            vat_amount=domain_invoice.vat_amount,
            total_amount=domain_invoice.total_amount
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
        logger.debug("Searching for invoice with number: %s", invoice_number)
        logger.debug("Type of invoice_number: %s", type(invoice_number))
        try:
            # Order by created_at descending and get the first one
            db_invoice = DjangoInvoice.objects.filter(
                invoice_number=invoice_number
            ).order_by('-created_at').first()

            if db_invoice:
                logger.debug("Found invoice in DB: %s", db_invoice)
                return self._to_domain(db_invoice)
            else:
                logger.debug("No invoice found with that number")
                return None

        except Exception as e:
            logger.error("Error retrieving invoice: %s", str(e))
            return None

    def list_by_status(self, status: str) -> List[DomainInvoice]:
        """List all invoices with a given status."""
        db_invoices = DjangoInvoice.objects.filter(status=status)
        return [self._to_domain(invoice) for invoice in db_invoices]

    def list_overdue(
        self, as_of: Optional[date] = None
    ) -> List[DomainInvoice]:
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
            
            # Get the manual urgency value if it exists
            manual_urgency_value = (
                invoice._manual_urgency.db_value
                if invoice._manual_urgency is not None
                else None
            )
            
            # Use model's update method for encapsulation
            db_invoice.update(
                amount=invoice.amount,
                due_date=invoice.due_date,
                status=invoice.status.value,
                uploaded_by_id=user_id,
                manual_urgency=manual_urgency_value
                
            )
            # Save the changes to the database
            db_invoice.save()
            return self._to_domain(db_invoice)
        except ObjectDoesNotExist as exc:
            raise InvalidInvoiceError(
                f"Invoice {invoice.invoice_number} not found"
            ) from exc


def list_by_urgency(self, urgency_level: UrgencyLevel) -> List[DomainInvoice]:
    """Retrieve invoices matching a specific urgency level.

    This method finds invoices with:
    1. A matching manual urgency OR
    2. A calculated urgency matching the requested level, based on due date

    Args:
        urgency_level: The urgency level to filter by

    Returns:
        List of domain invoice models with the specified urgency level
    """
    today = date.today()

    # First, find invoices with matching manual urgency
    db_invoices_with_manual = DjangoInvoice.objects.filter(
        manual_urgency=urgency_level.db_value
    )

    # Determine the date range based on urgency level
    min_days, max_days = urgency_level.day_range
    min_date = None if min_days is None else (today + timedelta(days=min_days))
    max_date = None if max_days is None else (today + timedelta(days=max_days))

    # Build query for calculated urgency (excluding manual overrides)
    calculated_query = Q(manual_urgency__isnull=True)

    if min_date is not None and max_date is not None:
        calculated_query &= Q(due_date__gte=min_date, due_date__lte=max_date)
    elif min_date is not None:
        calculated_query &= Q(due_date__gte=min_date)
    elif max_date is not None:
        calculated_query &= Q(due_date__lte=max_date)

    # Get invoices with calculated urgency
    db_invoices_calculated = DjangoInvoice.objects.filter(calculated_query)

    # Use `chain()` to lazily iterate without loading everything into memory
    db_invoices = chain(db_invoices_with_manual, db_invoices_calculated)

    # Convert to domain models
    return [self._to_domain(invoice) for invoice in db_invoices]


    def list_by_urgency_order(
        self, 
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[DomainInvoice]:
        """Retrieve invoices ordered by urgency level (highest to lowest).
        
        This method creates a prioritized list for cash flow planning,
        with most urgent invoices first.
        
        The ordering is:
        1. First by manual urgency (if set)
        2. Then by calculated urgency based on due date
        
        Args:
            status: Optional status filter (e.g., only pending invoices)
            limit: Optional maximum number of results to return
            
        Returns:
            List of domain invoice models ordered by urgency
        """
        # Start with base query
        query = DjangoInvoice.objects.all()
        
        # Apply status filter if provided
        if status:
            query = query.filter(status=status)
        
        # For proper sorting:
        # 1. Invoices with manual_urgency are ordered by that value
        # 2. Invoices without manual_urgency are ordered by due_date
        
        # Order by manual_urgency (null last), then by due_date
        db_invoices = query.order_by(
            models.F('manual_urgency').asc(nulls_last=True),
            'due_date'
        )
        
        # Apply limit if provided
        if limit:
            db_invoices = db_invoices[:limit]
            
        # Convert to domain models
        return [self._to_domain(invoice) for invoice in db_invoices]
