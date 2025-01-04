"""Coordinates the complete PDF transformation process."""

from datetime import datetime, date, timedelta
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
            print(f"\nStarting PDF transformation for: {pdf_path}")
            # Step 1: Extract text using OCR
            text_content = self.ocr_service.extract_text(pdf_path)
            print(f"\nExtracted text:\n{text_content}")

            # Step 2: Analyze text to extract fields
            raw_data = self.text_analyzer.extract_fields(text_content)
            print(f"\nExtracted raw data:\n{raw_data}")

            # String of pdf path
            pdf_path_str = str(pdf_path)

            # Step 3: Standardize the extracted data
            standardized = self._standardize_data(raw_data, pdf_path_str)
            print(f"\nStandardized data:\n{standardized}")

            # Return the standardized data
            return standardized

        except (OCRError, TextAnalysisError) as e:
            print(f"\nTransformation error: {str(e)}")
            raise PDFTransformationError(
                f"PDF transformation failed: {str(e)}"
            ) from e

    def _standardize_data(
        self, raw_data: Dict, file_path: str
    ) -> Dict[str, Any]:
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
            standardized = {
                'file_path': file_path
            }

            # Process invoice number
            if 'invoice_number' in raw_data:
                standardized['invoice_number'] = raw_data['invoice_number'].strip()

            # Process amount
            if 'amount' in raw_data:
                amount_str = raw_data['amount'].strip()
                # Handle European number formatting with comma decimals
                amount_str = amount_str.replace('.', '').replace(',', '.')
                standardized['amount'] = Decimal(amount_str)

            # Process date with more flexible parsing
            if 'date' in raw_data and raw_data['date']:
                date_str = raw_data['date'].strip()
                try:
                    # Remove ordinal indicators and extra whitespace
                    cleaned_date = (
                        date_str.replace('st', '')
                        .replace('nd', '')
                        .replace('rd', '')
                        .replace('th', '')
                        .strip()
                    )
                    
                    # Try parsing with various formats
                    for fmt in [
                        '%b %d %Y',      # Nov 5 2024
                        '%B %d %Y',      # November 5 2024
                        '%d-%m-%Y',      # 05-11-2024
                        '%d/%m/%Y',      # 05/11/2024
                        '%Y-%m-%d'       # 2024-11-05
                    ]:
                        try:
                            parsed_date = datetime.strptime(cleaned_date, fmt)
                            standardized['due_date'] = parsed_date.date()
                            break
                        except ValueError:
                            continue
                    
                    if 'due_date' not in standardized:
                        raise ValueError(f"Could not parse date: {date_str}")
                        
                except Exception as e:
                    print(f"Date parsing failed: {str(e)}")
                    # Set a default due date 30 days from now if parsing fails
                    standardized['due_date'] = date.today() + timedelta(days=30)

            return standardized

        except Exception as e:
            raise PDFTransformationError(
                f"Failed to standardize data: {str(e)}"
            ) from e
