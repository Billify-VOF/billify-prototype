"""Coordinates the complete PDF transformation process."""

import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Union
from integrations.transformers.pdf.ocr import OCRService, OCRError
from integrations.transformers.pdf.text_analysis import TextAnalyzer, TextAnalysisError
from datetime import date, datetime
from logging import getLogger

# Module-level logger
logger = getLogger(__name__)


class PDFTransformationError(Exception):
    """Raised when the overall PDF transformation process fails."""


class PDFTransformer:
    """Transforms PDFs into structured data via OCR and text analysis."""

    def __init__(self):
        """Initialize with required services."""
        self.ocr_service = OCRService()
        self.text_analyzer = TextAnalyzer()

    def transform(self, pdf_path: Path) -> Dict[str, Any]:
        """Transform a PDF into structured invoice data.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dict containing extracted invoice data

        Raises:
            PDFTransformationError: If the PDF cannot be processed or data extraction fails
        """
        try:
            logger.info("Starting PDF transformation for: %s", pdf_path)

            # Step 1: Extract text using OCR
            text_content = self.ocr_service.extract_text_from_pdf(pdf_path)
            logger.debug("Extracted text:\n%s", text_content)

            # Step 2: Analyze text to extract fields
            raw_data = self.text_analyzer.extract_fields(text_content)
            logger.debug("Extracted raw data:\n%s", raw_data)

            # Step 3: Extract file metadata (size, type, name)
            file_metadata = self.extract_file_metadata(pdf_path)

            # Step 4: Standardize extracted invoice data
            standardized = self._standardize_data(raw_data, file_metadata)
            logger.info("Standardized data:\n%s", standardized)

            return standardized

        except (OCRError, TextAnalysisError) as e:
            logger.error("Transformation error: %s", str(e))
            raise PDFTransformationError(f"PDF transformation failed: {str(e)}") from e

    def extract_file_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract metadata like file size, file type, and original name.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing file metadata.
        """
        try:
            file_size = os.path.getsize(pdf_path)  # File size in bytes
            file_name = pdf_path.name  # Extract original file name
            file_type = "PDF"

            return {
                "file_size": file_size,
                "file_name": file_name,
                "file_type": file_type,
            }

        except Exception as e:
            logger.error("Failed to extract file metadata: %s", str(e))
            raise PDFTransformationError(f"Failed to extract file metadata: {str(e)}") from e

    def _standardize_data(self, raw_data: Dict, file_metadata: Dict) -> Dict[str, Any]:
        """Convert raw extracted data into standardized invoice format.

        Args:
            raw_data: Dictionary containing extracted field values
            file_metadata: Dictionary containing extracted file metadata

        Returns:
            Dictionary with standardized invoice data
        """
        try:
            logger.info("Standardizing extracted data")
            standardized: Dict[str, Any] = {
                # File metadata
                "file_path": file_metadata.get("file_name", "UNKNOWN"),
                "file_size": file_metadata.get("file_size"),
                "file_type": file_metadata.get("file_type"),
                # Default values for required fields
                "invoice_number": raw_data.get("invoice_number", "UNKNOWN"),
                "amount": Decimal(raw_data.get("amount", "0.00")),
                "due_date": raw_data.get("due_date", date.today()),
                # Buyer & Seller Information
                "buyer_name": raw_data.get("buyer_name", ""),
                "buyer_address": raw_data.get("buyer_address", ""),
                "buyer_email": raw_data.get("buyer_email", ""),
                "buyer_vat": raw_data.get("buyer_vat", ""),
                "seller_name": raw_data.get("seller_name", ""),
                "seller_vat": raw_data.get("seller_vat", ""),
                # Payment & Transaction Details
                "payment_method": raw_data.get("payment_method", ""),
                "currency": raw_data.get("currency", ""),
                "iban": raw_data.get("iban", ""),
                "bic": raw_data.get("bic", ""),
                "payment_processor": raw_data.get("payment_processor", ""),
                "transaction_id": raw_data.get("transaction_id", ""),
                # Amounts
                "subtotal": Decimal(raw_data.get("subtotal", "0.00")),
                "vat_amount": Decimal(raw_data.get("vat_amount", "0.00")),
                "total_amount": Decimal(raw_data.get("total_amount", "0.00")),
            }

            self._validate_standardized_data(standardized)

            return standardized

        except Exception as e:
            logger.error("Failed to standardize data: %s", str(e))
            raise PDFTransformationError(f"Failed to standardize data: {str(e)}") from e

    def _validate_standardized_data(self, data: Dict) -> None:
        """Validate that standardized data meets minimum requirements.

        Args:
            data: Standardized data dictionary

        Raises:
            PDFTransformationError: If data fails validation
        """
        if data.get("amount", Decimal("0")) <= 0:
            logger.error("Invalid invoice amount: %s", data.get("amount"))
            raise PDFTransformationError("Invoice amount must be positive")

        if not data.get("invoice_number"):
            logger.error("Missing invoice number")
            raise PDFTransformationError("Invoice must have an invoice number")

        if not isinstance(data.get("due_date"), date):
            logger.error("Invalid due date: %s", data.get("due_date"))
            raise PDFTransformationError("Invoice must have a valid due date")
