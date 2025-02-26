"""Coordinates the complete PDF transformation process."""

import re
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Union
from integrations.transformers.pdf.ocr import OCRService, OCRError
from integrations.transformers.pdf.text_analysis import (
    TextAnalyzer,
    TextAnalysisError
)
from datetime import date
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
            PDFTransformationError: If the PDF cannot be processed or data
                extracted
        """
        try:
            logger.info("Starting PDF transformation for: %s", pdf_path)
            # Step 1: Extract text using OCR
            # Old method using pdf2image
            # text_content = self.ocr_service.extract_text(pdf_path)
            # New method using pdfplumber
            text_content = self.ocr_service.extract_text_from_pdf(
                pdf_path
            )
            logger.debug("Extracted text:\n%s", text_content)

            # Step 2: Analyze text to extract fields
            raw_data = self.text_analyzer.extract_fields(text_content)
            logger.debug("Extracted raw data:\n%s", raw_data)

            # String of pdf path
            pdf_path_str = str(pdf_path)

            # Step 3: Standardize the extracted data
            standardized = self._standardize_data(raw_data, pdf_path_str)
            logger.info("Standardized data:\n%s", standardized)

            # Return the standardized data
            return standardized

        except (OCRError, TextAnalysisError) as e:
            logger.error("Transformation error: %s", str(e))
            raise PDFTransformationError(
                f"PDF transformation failed: {str(e)}"
            ) from e

    def _standardize_data(
        self, raw_data: Dict, file_path: str
    ) -> Dict[str, Union[str, Decimal, date]]:
        """
        Convert raw extracted data into our standard invoice format.

        This method ensures all extracted data follows our domain model's
        expectations, with proper typing and formatting.

        Args:
            raw_data: Dictionary containing extracted field values
            file_path: Path to the original PDF file

        Returns:
            Dictionary with standardized invoice data

        Raises:
            PDFTransformationError: If standardization fails
        """

        try:
            logger.info("Standardizing extracted data")
            standardized: Dict[str, Union[str, Decimal, date]] = {
                'file_path': file_path,
                # Add default values for required fields
                'invoice_number': 'UNKNOWN',
                'amount': Decimal('0.00'),
                'due_date': date.today()  # Default to today
            }

            # Process invoice number if available
            if raw_data.get('invoice_number'):
                invoice_number = raw_data['invoice_number'].strip()
                standardized['invoice_number'] = invoice_number
                logger.debug("Standardized invoice_number: %s", invoice_number)
            else:
                logger.warning("No invoice number found in extracted data")

            # Process amount if available
            if raw_data.get('amount'):
                amount_str = raw_data['amount'].strip()
                format_type = 'belgian' if ',' in amount_str else 'english'
                std_amount = self.text_analyzer.standardize_amount(
                    amount_str, format_type
                )
                standardized['amount'] = Decimal(std_amount)
                logger.debug("Standardized amount: %s", std_amount)
            else:
                logger.warning("No amount found in extracted data")

            # Process date with more flexible parsing
            if raw_data.get('date'):
                date_str = raw_data['date'].strip()
                date_pattern = r'\d{2}[-/]\d{2}[-/]\d{4}'
                is_belgian = re.match(date_pattern, date_str)
                format_type = 'belgian' if is_belgian else 'english'
                std_date = self.text_analyzer.standardize_date(
                    date_str, format_type
                )
                if std_date:
                    year, month, day = map(int, std_date.split('-'))
                    standardized['due_date'] = date(year, month, day)
                    logger.debug("Standardized due_date: %s", std_date)
                else:
                    logger.warning("Could not parse date format")
            else:
                logger.warning("No date found in extracted data")

            # Process supplier name if available
            if raw_data.get('supplier_name'):
                supplier = raw_data['supplier_name'].strip()
                standardized['supplier_name'] = supplier
                logger.debug("Standardized supplier_name: %s", supplier)
            else:
                # Supplier name is optional
                standardized['supplier_name'] = ''
                logger.info("No supplier name found in extracted data")

            # Validate that we have minimum required data
            self._validate_standardized_data(standardized)

            return standardized

        except Exception as e:
            logger.error("Failed to standardize data: %s", str(e))
            raise PDFTransformationError(
                f"Failed to standardize data: {str(e)}"
            ) from e

    def _validate_standardized_data(self, data: Dict) -> None:
        """
        Validate that standardized data meets minimum requirements.

        Args:
            data: Standardized data dictionary

        Raises:
            PDFTransformationError: If data fails validation
        """
        # Check amount is positive
        if data.get('amount', Decimal('0')) <= 0:
            logger.error("Invalid invoice amount: %s", data.get('amount'))
            raise PDFTransformationError(
                "Invoice amount must be positive"
            )

        # Check invoice number is not empty
        if not data.get('invoice_number'):
            logger.error("Missing invoice number")
            raise PDFTransformationError(
                "Invoice must have an invoice number"
            )

        # Check due date is valid
        if not isinstance(data.get('due_date'), date):
            logger.error("Invalid due date: %s", data.get('due_date'))
            raise PDFTransformationError(
                "Invoice must have a valid due date"
            )
