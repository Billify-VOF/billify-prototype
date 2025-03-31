from django.test import TestCase
from application.services.invoice_service import InvoiceProcessingService
from domain.services.invoice_service import InvoiceService
from domain.repositories.interfaces.invoice_repository import InvoiceRepository
from domain.repositories.interfaces.storage_repository import StorageRepository
from integrations.transformers.pdf.transformer import PDFTransformer
from pathlib import Path
from unittest.mock import Mock

# from unittest.mock import patch, MagicMock, Mock


class TestInvoiceProcessing(TestCase):
    """Test cases for InvoiceProcessingService"""

    def setUp(self):
        """Set up dependencies for invoice processing using mocks"""
        # Create mock services and repositories instead of real implementations
        self.invoice_service = Mock(spec=InvoiceService)
        self.invoice_repository = Mock(spec=InvoiceRepository)
        self.storage_repository = Mock(spec=StorageRepository)

        # Configure basic mock behaviors
        self.storage_repository.save_file.return_value = "test_path"
        self.storage_repository.get_file_path.return_value = "full_test_path"

        # Create mock PDF transformer directly
        self.pdf_transformer_mock = Mock(spec=PDFTransformer)

        # Create processing service with mocks
        self.processing_service = InvoiceProcessingService(
            self.invoice_service, self.invoice_repository, self.storage_repository
        )

        # Replace the transformer with our mock
        self.processing_service.pdf_transformer = self.pdf_transformer_mock

        # Sample path for testing
        self.sample_pdf = Path("backend/infrastructure/django/repositories/sample.pdf")

    # @patch("integrations.transformers.pdf.transformer.PDFTransformer")
    # def test_process_invoice_success(self, mock_pdf_transformer):
    #     """Test successful invoice processing with comprehensive assertions"""
    #     # Prepare more complete sample invoice data
    #     sample_invoice_data = {
    #         "invoice_number": "INV-001",
    #         "subtotal": "180.00",
    #         "vat_amount": "20.00",
    #         "total_amount": "200.00",
    #         "due_date": "2025-04-01",
    #         "buyer_name": "John Doe",
    #         "buyer_address": "123 Main St",
    #         "buyer_email": "john@example.com",
    #         "buyer_vat": "VAT123456",
    #         "seller_name": "XYZ Corp",
    #         "seller_vat": "VAT654321",
    #         "payment_method": "bank_transfer",
    #         "currency": "USD",
    #         "iban": "US123456789",
    #         "bic": "BANKUS12",
    #         "payment_processor": None,
    #         "transaction_id": None,
    #     }

    #     # Configure the PDF transformer mock
    #     mock_pdf_transformer.return_value.transform.return_value = sample_invoice_data

    #     # Create a mocked file
    #     file_mock = MagicMock()
    #     file_mock.name = "test_invoice.pdf"

    #     # Configure the invoice service to return a mocked domain object
    #     mock_invoice = Mock()
    #     mock_invoice.id = 42
    #     mock_invoice.invoice_number = "INV-001"
    #     mock_invoice.status = "pending"
    #     mock_invoice.is_updated = False
    #     self.invoice_service.process_invoice.return_value = mock_invoice

    #     # Configure urgency info
    #     self.invoice_service.get_urgency_info.return_value = {"days_until_due": 30, "priority": "normal"}

    #     # Configure storage path for testing
    #     with patch("os.path.getsize", return_value=102400):
    #         with patch("mimetypes.guess_type", return_value=["application/pdf"]):
    #             # Call the method being tested
    #             result = self.processing_service.process_invoice(file_mock, user_id=1)

    #     # Verify all important fields in the result
    #     self.assertEqual(result["invoice_id"], 42)
    #     self.assertEqual(result["invoice_number"], "INV-001")
    #     self.assertEqual(result["status"], "pending")
    #     self.assertEqual(result["updated"], False)

    #     # Verify all metadata fields from invoice data
    #     self.assertEqual(result["buyer_name"], "John Doe")
    #     self.assertEqual(result["buyer_address"], "123 Main St")
    #     self.assertEqual(result["buyer_email"], "john@example.com")
    #     self.assertEqual(result["buyer_vat"], "VAT123456")
    #     self.assertEqual(result["seller_name"], "XYZ Corp")
    #     self.assertEqual(result["seller_vat"], "VAT654321")
    #     self.assertEqual(result["payment_method"], "bank_transfer")
    #     self.assertEqual(result["currency"], "USD")
    #     self.assertEqual(result["iban"], "US123456789")
    #     self.assertEqual(result["bic"], "BANKUS12")
    #     self.assertEqual(result["subtotal"], "180.00")
    #     self.assertEqual(result["vat_amount"], "20.00")
    #     self.assertEqual(result["total_amount"], "200.00")

    #     # Verify file metadata
    #     self.assertEqual(result["file_size"], 102400)
    #     self.assertEqual(result["file_type"], "application/pdf")
    #     self.assertEqual(result["original_file_name"], "test_invoice.pdf")

    #     # Verify urgency info
    #     self.assertEqual(result["urgency"]["days_until_due"], 30)
    #     self.assertEqual(result["urgency"]["priority"], "normal")

    #     # Verify correct method calls
    #     self.pdf_transformer_mock.transform.assert_called_once()
    #     self.invoice_service.process_invoice.assert_called_once()
    #     self.invoice_service.get_urgency_info.assert_called_once_with(mock_invoice)

    # def test_process_invoice_failure(self):
    #     """Test processing failure due to OCR error"""
    #     with patch.object(
    #         self.processing_service.pdf_transformer, "transform", side_effect=Exception("OCR error")
    #     ):
    #         file_mock = MagicMock()
    #         with self.assertRaises(Exception) as context:
    #             self.processing_service.process_invoice(file_mock, user_id=1)
    #         self.assertIn("OCR error", str(context.exception))
