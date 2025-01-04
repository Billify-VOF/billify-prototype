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
            print("TextAnalyzer: Starting field extraction")
            print(f"Text Analysis: Input text:\n{text}")
            patterns = {
                'invoice_number': r'(?:Factuur|Facture):?\s*([0-9]{4}[-./][0-9]{3,4})',
                'amount': r'(?:Totaal|Total):?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*(?:EUR|€)',
                'date': r'(?:Documentdatum|Date du document):?\s*(\d{2}[-/]\d{2}[-/]\d{4})',
                'supplier_name': r'^([^\n]+?(?:CommV|BV|BVBA|SA|SPRL|NV)?\b)'
            }
            extracted = self._extract_using_patterns(text, patterns)
            print(f"TextAnalyzer: Extracted fields: {extracted}")
            return extracted
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
            match = re.search(pattern, text, re.IGNORECASE)
            print(f"\nTrying to match {field} with pattern: {pattern}")
            if match:
                extracted[field] = match.group(1)
                print(f"Found match for {field}: {match.group(1)}")
            else:
                print(f"No match found for {field}")
        return extracted
