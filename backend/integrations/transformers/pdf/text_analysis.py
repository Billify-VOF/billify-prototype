"""Text analysis service for identifying invoice fields in extracted text."""

import re
from typing import Dict, Optional
from dateutil.parser import parse


class TextAnalysisError(Exception):
    """Raised when field extraction from text fails."""


class TextAnalyzer:
    """Extracts structured data from invoice text using pattern matching."""

    def __init__(self):
        self.patterns = {
            'invoice_number': (
                r'(?:Factuur|Facture|Invoice Number|Invoice number|'
                r'Invoice ID|Receipt number|Numero de la factura|'
                r'N°\s*(?:de\s*)?factura|N°\s*de\s*referencia|Reference|'
                r'Order number|Booking\s*Reference|#\|)'
                r':?\s*([\w.-]+)'
            ),
            'amount': (
                r'(?:Total (?:Due|price|cost|amount|:)?|Total|Amount Due|'
                r'Grand\s*Total|Net to pay|Subtotal|Totaal|€|EUR|\$)\s*'
                r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
            ),
            'date': (
                r'(?:Documentdatum|Date du document|Date|Invoice date|'
                r'Date of issue|Date due|Issued|Due|Payment date|Date paid|'
                r'Paid on|Fecha|Fecha del pedido|(?:Order|Payment) date)'
                r':?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|[A-Za-z]{3,9}\.? '
                r'\d{1,2},?\s?\d{4}|\d{1,2}/\d{1,2}/\d{2,4})'
            ),
            'supplier_name': (
                r'(?:Payable to|Invoiced to|Billed to|From|'
                r'Factuur|Sold by|Vendido por|Provider|Vendor|Supplier)'
                r':?\s*([\w\s,.]+?(?:CommV|BV|BVBA|SA|SPRL|NV|Inc\.|LLC|'
                r'Autonomo|NIF)?\b)'
            ),
            'due_date': (
                r'(?:Due date|Payment due|Betalen voor|Vervaldatum)'
                r':?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4}|[A-Za-z]{3,9}\.? '
                r'\d{1,2},?\s?\d{4}|\d{1,2}/\d{1,2}/\d{2,4})'
            )
        }

    def extract_fields(self, text: str) -> Dict:
        """Extract structured field data from raw text."""
        try:
            print("TextAnalyzer: Starting field extraction")
            print(f"Text Analysis: Input text:\n{text}")

            extracted = self._extract_using_patterns(text, self.patterns)

            # If date not found, fallback parse
            if not extracted.get('date'):
                fallback = self._fallback_extract_date(text)
                if fallback:
                    extracted['date'] = fallback

            # If due_date not found, set default (same as date)
            if not extracted.get('due_date'):
                extracted['due_date'] = extracted.get('date')

            print(f"TextAnalyzer: Extracted fields: {extracted}")
            return extracted

        except Exception as e:
            raise TextAnalysisError(f"Failed to extract fields: {e}") from e

    def validate_extracted_fields(self, fields: Dict) -> bool:
        """Verify that all required fields were extracted successfully."""
        # Relax required fields if invoice_number or date are optional
        # or just {'amount'} if you prefer
        required_fields = {'invoice_number', 'amount', 'date'}
        return all(
            field in fields and fields[field] for field in required_fields
        )

    def _extract_using_patterns(self, text: str, patterns: Dict) -> Dict:
        """Apply regex patterns to extract fields."""
        extracted = {}
        # -- Moved the 'return' below so we gather *all* fields --
        for field, pattern in patterns.items():
            print(f"\nTrying to match {field} with pattern: {pattern}")
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1)
                print(f"Found match for {field}: {extracted[field]}")
            else:
                print(f"No match found for {field}")
        return extracted   # Return *after* the loop finishes all fields.

    def _fallback_extract_date(self, text: str) -> Optional[str]:
        """Second pass for date if labeled pattern fails."""
        lines = text.splitlines()
        for line in lines:
            # If you wish to skip lines that *clearly* aren't date-like,
            # uncomment this check:
            #
            # if not re.search(
            #     r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'
            #     r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            #     line, re.IGNORECASE
            # ):
            #     continue
            try:
                dt = parse(line, fuzzy=True)
                # If parsing is successful, return the first parse you get.
                return dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError) as e:
                print(f"Failed to parse date from line '{line}': {e}")
        return None

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

    def standardize_date(
        self, date_str: str, format_type: str
    ) -> Optional[str]:
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
            # Convert English format (e.g. Dec 7th 2024) to ISO
            try:
                date_obj = parse(date_str)
                return date_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError) as e:
                print(f"Failed to parse date: {e}")
                return None

        return None
