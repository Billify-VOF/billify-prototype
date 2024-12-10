"""Text analysis service for identifying invoice fields in extracted text."""

import re
from typing import Dict


class TextAnalysisError(Exception):
    """Raised when field extraction from text fails."""


class TextAnalyzer:
    """Extracts structured data from invoice text using pattern matching."""

    def extract_fields(self, text: str) -> Dict:
        """Extract structured field data from raw text."""
        try:
            patterns = {
                'invoice_number': r'Invoice\s*#?\s*(\w+[-]?\d+)',
                'amount': r'Total[\s:]*[$€£]?\s*(\d+[.,]\d{2})',
                'date': r'Date[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                'supplier_name': r'Company[\s:]*(.+)'
            }

            return self._extract_using_patterns(text, patterns)
        except Exception as e:
            raise TextAnalysisError(
                f"Failed to extract fields: {str(e)}"
            ) from e

    def validate_extracted_fields(self, fields: Dict) -> bool:
        """Verify that all required fields were extracted successfully."""
        required_fields = {'invoice_number', 'amount', 'date'}
        return all(field in fields for field in required_fields)

    def _extract_using_patterns(self, text: str, patterns: Dict) -> Dict:
        """Apply regex patterns to extract fields."""
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                extracted[field] = match.group(1)
        return extracted
