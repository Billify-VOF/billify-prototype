from domain.models.value_objects import InvoiceStatus

def test_save_and_retrieve(invoice_repo, sample_invoice):
    saved = invoice_repo.save(sample_invoice, 1)
    retrieved = invoice_repo.get_by_id(saved.id)
    assert retrieved.invoice_number == "INV-001"

def test_status_updates(invoice_repo, sample_invoice):
    sample_invoice.mark_as_paid()
    saved = invoice_repo.save(sample_invoice, 1)
    assert saved.status == InvoiceStatus.PAID