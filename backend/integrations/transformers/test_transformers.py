import unittest
from pathlib import Path
from integrations.transformers.pdf.transformer import PDFTransformer, PDFTransformationError


class TestPDFTransformer(unittest.TestCase):
    """Test cases for PDFTransformer"""

    def setUp(self):
        """Set up the test environment"""
        self.transformer = PDFTransformer()
        self.sample_pdf = Path("backend/infrastructure/django/repositories/sample.pdf")

    def test_extract_text_success(self):
        """Test that OCR extracts text without errors"""
        text = self.transformer.ocr_service.extract_text_from_pdf(self.sample_pdf)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 10)  # Ensure some text is extracted

    def test_transform_pdf_success(self):
        """Test complete transformation of a sample PDF"""
        result = self.transformer.transform(self.sample_pdf)
        self.assertIsInstance(result, dict)
        self.assertIn("invoice_number", result)
        self.assertIn("amount", result)
        self.assertIn("file_size", result)
        self.assertIn("file_type", result)
        self.assertIn("buyer_name", result)

    def test_missing_file_error(self):
        """Test that a missing file raises an error"""
        with self.assertRaises(PDFTransformationError):
            self.transformer.transform(Path("non_existent_file.pdf"))
