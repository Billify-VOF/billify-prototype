from django.test import TestCase
from application.services.invoice_service import InvoiceProcessingService
from domain.services.invoice_service import InvoiceService
from infrastructure.django.repositories.invoice_repository import DjangoInvoiceRepository
from infrastructure.storage.file_system import FileStorageService
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestInvoiceProcessing(TestCase):
    """Test cases for InvoiceProcessingService"""

    def setUp(self):
        """Set up dependencies for invoice processing"""
        self.invoice_service = InvoiceService()
        self.invoice_repository = DjangoInvoiceRepository()
        self.storage_repository = FileStorageService()
        self.processing_service = InvoiceProcessingService(
            self.invoice_service, self.invoice_repository, self.storage_repository
        )
        self.sample_pdf = Path("backend/infrastructure/django/repositories/sample.pdf")

    @patch("integrations.transformers.pdf.transformer.PDFTransformer")
    def test_process_invoice_success(self, mock_pdf_transformer):
        """Test successful invoice processing"""
        mock_pdf_transformer.return_value.transform.return_value = {
            "invoice_number": "INV-001",
            "amount": "200.00",
            "due_date": "2025-04-01",
            "file_path": str(self.sample_pdf),
            "file_size": 102400,
            "file_type": "PDF",
            "buyer_name": "John Doe",
            "seller_name": "XYZ Corp",
        }

        file_mock = MagicMock()
        result = self.processing_service.process_invoice(file_mock, user_id=1)

        self.assertEqual(result["invoice_number"], "INV-001")
        self.assertEqual(result["amount"], "200.00")
        self.assertEqual(result["buyer_name"], "John Doe")
        self.assertEqual(result["seller_name"], "XYZ Corp")

    def test_process_invoice_failure(self):
        """Test processing failure due to OCR error"""
        with patch.object(
            self.processing_service.pdf_transformer, "transform", side_effect=Exception("OCR error")
        ):
            file_mock = MagicMock()
            with self.assertRaises(Exception) as context:
                self.processing_service.process_invoice(file_mock, user_id=1)
            self.assertIn("OCR error", str(context.exception))
