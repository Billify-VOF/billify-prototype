import pytest
from decimal import Decimal
from datetime import date
from domain.models.invoice import Invoice
from domain.models.value_objects import InvoiceStatus


class TestInvoiceRepository:

    def __init__(self):
        self.invoices = {}
        self.next_id = 1

    def save(self, invoice, user_id):
        if not invoice.id:
            invoice.id = self.next_id
            self.next_id += 1
        self.invoices[invoice.id] = invoice
        return invoice

    def get_by_id(self, invoice_id):
        return self.invoices.get(invoice_id)


@pytest.fixture
def invoice_repo():
    return TestInvoiceRepository()

@pytest.fixture
def sample_invoice():
    return Invoice.create(
        amount=Decimal("1000.00"),
        due_date=date.today(),
        invoice_number="INV-001"
    )