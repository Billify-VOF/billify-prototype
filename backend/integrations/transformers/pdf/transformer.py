"""Coordinates the complete PDF transformation process."""

import os
import re
import mimetypes
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any
from integrations.transformers.pdf.ocr import OCRService, OCRError
from integrations.transformers.pdf.text_analysis import TextAnalyzer, TextAnalysisError
from datetime import date
from logging import getLogger

# Module-level logger
logger = getLogger(__name__)

# Import dateutil at module level with type ignore
try:
    from dateutil.parser import parse as parse_date  # type: ignore
except ImportError:
    parse_date = None
    logger.warning("dateutil module not available, date parsing will be limited")


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
            file_type = mimetypes.guess_type(str(pdf_path))[0] or "application/pdf"

            return {
                "file_size": file_size,
                "file_name": file_name,
                "file_type": file_type,
            }

        except Exception as e:
            logger.error("Failed to extract file metadata: %s", str(e))
            raise PDFTransformationError(f"Failed to extract file metadata: {str(e)}") from e

    def _standardize_amount(self, amount_str: str) -> str:
        """Convert European number format to standard decimal format.

        Args:
            amount_str: Amount string potentially in European format

        Returns:
            Standardized amount string
        """
        if amount_str.find(".") >= 0 and amount_str.find(",") >= 0:
            # If the amount string contains both `.` and `,`,
            # we need to determine which one serves as the decimal symbol.
            splits = re.split(r"[,.]", amount_str)
            whole_number = int("".join(splits[:-1]))
            fractional_number = int(splits[-1])
            amount_str = str(whole_number) + "." + str(fractional_number)
        elif amount_str.find(".") >= 0 and amount_str.find(",") == -1:
            # If the amount string contains only `.`
            if amount_str.count(".") > 1:
                # If amount string has multiple `.`, that means `.` is thousand separator
                amount_str = amount_str.replace(".", "")
            # The other case is amount string has only one `.`, and this is normal cause it's decimal point
        elif amount_str.find(",") >= 0 and amount_str.find(".") == -1:
            # If the amount string contains only `,`
            if amount_str.count(",") > 1:
                # If amount string has multiple `,`, that means `,` is thousand separator
                amount_str = amount_str.replace(",", "")
            elif amount_str.count(",") == 1:
                # If amount string has only one `,`, then it means decimal point
                amount_str = amount_str.replace(",", ".")
        return amount_str

    def _standardize_data(self, raw_data: Dict, file_metadata: Dict) -> Dict[str, Any]:
        """Standardize extracted fields to a consistent format.

        Args:
            raw_data: Extracted raw data from PDF
            file_metadata: Metadata about the file

        Returns:
            Dict with standardized values

        Raises:
            PDFTransformationError: If standardization fails
        """
        try:
            logger.info("Standardizing extracted data")

            # Standardize amounts
            subtotal = self._standardize_amount(raw_data.get("subtotal", "0.00"))
            vat_amount = self._standardize_amount(raw_data.get("vat_amount", "0.00"))
            total_amount = self._standardize_amount(raw_data.get("total_amount", "0.00"))

            # Parse and convert dates from various formats
            due_date = raw_data.get("due_date")
            parsed_due_date = date.today()  # Default to today

            if due_date and isinstance(due_date, str):
                # Try to parse European format (DD/MM/YYYY)
                if re.match(r"\d{1,2}/\d{1,2}/\d{4}", due_date):
                    try:
                        day, month, year = due_date.split("/")
                        parsed_due_date = date(int(year), int(month), int(day))
                        logger.info(
                            "Successfully parsed European date format: %s -> %s", due_date, parsed_due_date
                        )
                    except (ValueError, TypeError) as e:
                        logger.warning("Failed to parse European date format: %s - %s", due_date, str(e))
                # Try standard date parsing for other formats
                elif parse_date is not None:
                    try:
                        parsed_due_date = parse_date(due_date).date()
                        logger.info(
                            "Successfully parsed date using dateutil: %s -> %s", due_date, parsed_due_date
                        )
                    except (ValueError, TypeError) as e:
                        logger.warning("Failed to parse date using dateutil: %s - %s", due_date, str(e))

            standardized: Dict[str, Any] = {
                # File metadata
                "file_path": file_metadata.get("file_name", "UNKNOWN"),
                "file_size": file_metadata.get("file_size"),
                "file_type": file_metadata.get("file_type"),
                # Default values for required fields
                "invoice_number": raw_data.get("invoice_number", ""),
                "due_date": parsed_due_date,
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
                "subtotal": Decimal(subtotal),
                "vat_amount": Decimal(vat_amount),
                "total_amount": Decimal(total_amount),
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
        if data.get("total_amount", Decimal("0")) <= 0:
            logger.error("Invalid invoice total amount: %s", data.get("total_amount"))
            raise PDFTransformationError("Invoice total amount must be positive")

        if not data.get("invoice_number"):
            logger.error("Missing invoice number")
            raise PDFTransformationError("Invoice must have an invoice number")

        if not isinstance(data.get("due_date"), date):
            logger.error("Invalid due date: %s", data.get("due_date"))
            raise PDFTransformationError("Invoice must have a valid due date")
