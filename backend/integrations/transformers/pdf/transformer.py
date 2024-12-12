"""Coordinates the complete PDF transformation process."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Any
from integrations.transformers.pdf.ocr import OCRService, OCRError
from integrations.transformers.pdf.text_analysis import (
    TextAnalyzer,
    TextAnalysisError
)


class PDFTransformationError(Exception):
    """Raised when the overall PDF transformation process fails."""


class PDFTransformer:
    """Transforms PDFs into structured data via OCR and text analysis."""

    def __init__(self):
        """Initialize with required services."""
        self.ocr_service = OCRService()
        self.text_analyzer = TextAnalyzer()

    def transform(self, pdf_path: Path) -> Dict[str, Any]:
        """Transform a PDF invoice into structured data."""
        try:
            # Step 1: Extract text using OCR
            text_content = self.ocr_service.extract_text(pdf_path)

            # Step 2: Analyze text to extract fields
            raw_data = self.text_analyzer.extract_fields(text_content)

            # Step 3: Standardize the extracted data
            return self._standardize_data(raw_data)

        except (OCRError, TextAnalysisError) as e:
            raise PDFTransformationError(
                f"PDF transformation failed: {str(e)}"
            ) from e

    def _standardize_data(self, raw_data: Dict) -> Dict[str, Any]:
        """
        Convert raw extracted data into our standard invoice format.

        This method ensures all extracted data follows our domain model's
        expectations, with proper typing and formatting.

        Args:
            raw_data: Dictionary containing extracted field values

        Returns:
            Dictionary with standardized invoice data

        Raises:
            PDFTransformationError: If standardization fails
        """

        try:
            standardized = {}

            # Process invoice number
            if 'invoice_number' in raw_data:
                standardized['invoice_number'] = (
                    raw_data['invoice_number'].strip()
                )

            # Process amount - convert to Decimal and handle different formats
            if 'amount' in raw_data:
                amount_str = raw_data['amount'].replace(',', '.')
                try:
                    standardized['amount'] = Decimal(amount_str)
                except InvalidOperation as exc:
                    raise PDFTransformationError(
                        f"Invalid amount format: {amount_str}"
                    ) from exc

            # Process date - convert to ISO format
            if 'date' in raw_data:
                try:
                    # Try multiple date formats
                    for fmt in (
                        '%d-%m-%Y',
                        '%d/%m/%Y',
                        '%Y-%m-%d'
                    ):
                        try:
                            parsed_date = datetime.strptime(
                                raw_data['date'],
                                fmt
                            )
                            standardized['date'] = parsed_date.date()
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    raise PDFTransformationError(
                        f"Invalid date format: {str(e)}"
                    ) from e

            # Add supplier information if available
            if 'supplier_name' in raw_data:
                standardized['supplier_name'] = (
                    raw_data['supplier_name'].strip()
                )

            # Validate required fields
            required_fields = {'invoice_number', 'amount', 'date'}
            missing_fields = required_fields - set(standardized.keys())
            if missing_fields:
                raise PDFTransformationError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            return standardized

        except Exception as e:
            raise PDFTransformationError(
                f"Failed to standardize data: {str(e)}"
            ) from e
