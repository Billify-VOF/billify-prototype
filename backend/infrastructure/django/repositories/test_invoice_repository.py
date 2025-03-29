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
            amount=Decimal("100.50"),
            due_date=date.today(),
            buyer=BuyerInfo(name="Test Buyer"),
            seller=SellerInfo(name="Test Vendor"),
            payment=PaymentInfo(total_amount=Decimal("110.50")),
            file=FileInfo(path="test_file.pdf")
        )

        saved_invoice = self.repository.save(invoice, user_id=1)
        
        self.assertIsInstance(saved_invoice, DomainInvoice)
        
        self.assertEqual(saved_invoice.invoice_number, "INV-12345")
        self.assertEqual(saved_invoice.amount, Decimal("100.50"))
        self.assertEqual(saved_invoice.buyer.name, "Test Buyer")
        self.assertEqual(saved_invoice.seller.name, "Test Vendor")
        
        db_invoice = DjangoInvoice.objects.get(invoice_number="INV-12345")
        self.assertIsNotNone(db_invoice)

    def test_get_invoice_by_number(self):
        """Test retrieving an invoice by number"""
        DjangoInvoice.objects.create(
            invoice_number="INV-67890",
            amount=Decimal("50.75"),
            due_date=date.today(),
            uploaded_by=self.test_user,
            file_path="backend/infrastructure/django/repositories/sample.pdf",
        )

        fetched_invoice = self.repository.get_by_number("INV-67890")
        self.assertIsNotNone(fetched_invoice)
        self.assertEqual(fetched_invoice.invoice_number, "INV-67890")
