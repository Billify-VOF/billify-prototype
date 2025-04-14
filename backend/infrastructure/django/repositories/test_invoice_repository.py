from django.test import TestCase
from domain.models.invoice import Invoice as DomainInvoice
from infrastructure.django.models.invoice import Invoice as DjangoInvoice
from infrastructure.django.repositories.invoice_repository import DjangoInvoiceRepository
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from domain.models.invoice import BuyerInfo, SellerInfo, PaymentInfo, FileInfo


class TestInvoiceRepository(TestCase):
    """Test cases for DjangoInvoiceRepository"""

    def setUp(self):
        """Create test invoice repository and test user"""
        self.repository = DjangoInvoiceRepository()
        User = get_user_model()
        self.test_user = User.objects.create_user(id=1, username="abdul", password="password123")

    def test_save_invoice(self):
        """Test saving an invoice in the repository"""
        invoice = DomainInvoice.create(
            invoice_number="INV-12345",
            total_amount=Decimal("100.50"),
            due_date=date.today(),
            buyer=BuyerInfo(name="Test Buyer"),
            seller=SellerInfo(name="Test Vendor"),
            payment=PaymentInfo(total_amount=Decimal("100.50")),
            file=FileInfo(path="test_file.pdf"),
        )

        saved_invoice = self.repository.save(invoice, user_id=1)

        self.assertIsInstance(saved_invoice, DomainInvoice)

        self.assertEqual(saved_invoice.invoice_number, "INV-12345")
        self.assertEqual(saved_invoice.total_amount, Decimal("100.50"))
        self.assertEqual(saved_invoice.buyer.name, "Test Buyer")
        self.assertEqual(saved_invoice.seller.name, "Test Vendor")

        db_invoice = DjangoInvoice.objects.get(invoice_number="INV-12345")
        self.assertIsNotNone(db_invoice)
