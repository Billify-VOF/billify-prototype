from decimal import Decimal
from datetime import date
from domain.services.invoice_service import InvoiceService


def test_full_workflow(invoice_repo):
    service = InvoiceService()
    service.invoice_repo = invoice_repo

    data = {
        'amount': Decimal("2000.00"),
        'due_date': date.today(),
        'invoice_number': "INV-002"
    }
    invoice = service.create(data)
    saved = invoice_repo.save(invoice, 1)
    assert saved.id is not None