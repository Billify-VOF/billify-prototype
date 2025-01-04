"""Text analysis service for identifying invoice fields in extracted text."""

import re
from typing import Dict
from dateutil.parser import parse


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
                'invoice_number': r'(?:Factuur|Facture|Invoice Number):?\s*([0-9]{4}[-./][0-9]{3,4}|[0-9]+)',
                'amount': r'(?:Totaal|Total|Amount Due):?\s*(?:USD\s*)?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))\s*(?:EUR|€|USD|\$)?',
                'date': r'(?:Documentdatum|Date du document|Date):?\s*(\d{2}[-/]\d{2}[-/]\d{4}|[A-Za-z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
                'supplier_name': r'^([^\n]+?(?:CommV|BV|BVBA|SA|SPRL|NV|Inc\.|LLC)?\b)'
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

    def standardize_amount(self, amount_str: str, format_type: str) -> str:
        """
        Standardize amount based on detected format.
        """
        # Remove currency symbols and whitespace
        amount_str = re.sub(r'[€$\s]', '', amount_str)
        
        if format_type == 'belgian':
            # Convert Belgian format (1.815,00) to standard decimal
            if ',' in amount_str:
                amount_str = amount_str.replace('.', '').replace(',', '.')
        else:
            # English format is already standard decimal
            pass
        
        return amount_str

    def standardize_date(self, date_str: str, format_type: str) -> str:
        """
        Convert date to ISO format based on detected format.
        """
        if format_type == 'belgian':
            # Convert DD-MM-YYYY to ISO
            match = re.match(r'(\d{2})[-/](\d{2})[-/](\d{4})', date_str)
            if match:
                day, month, year = match.groups()
                return f"{year}-{month}-{day}"
        else:
            # Convert English format (Dec 7th 2024) to ISO
            try:
                date_obj = parse(date_str)
                return date_obj.strftime('%Y-%m-%d')
            except:
                return None
        
        return None
