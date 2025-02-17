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
                # r'(?:Factura|Facture|Invoice Number|Invoice number|Invoice|Document No.|Document number |Order|'
                # r'Invoice ID|Receipt number|Numero de la factura|Document No.|Document number|'
                # r'N°\s*(?:de\s*)?factura|N°\s*de\s*referencia|Reference|'
                # r'Order number|Booking\s*Reference|#\s*)'  # Matches common invoice-related labels
                # r'[:?\s]*'  # Matches optional spaces and punctuation after the label
                # r'(?:\n?\s*)'  # Allows for optional newline and spaces between label and number
                # r'(#?\d{1,}-?\d{1,}-?\d{1,}|\w{1,}\d+|\d{1,})'  
                r'(?:Invoice\s*(?:Number|ID)|Factura|Invoice|Order|Facture|Receipt\s*(?:Number)?|Numero\s*de\s*la\s*factura|Order number)'  # General invoice labels
                r'[:?\s]*'  # Matches optional spaces and punctuation after the label
                r'(?:\s*)'  # Allows optional spaces between label and number
                r'(#\s*\d{1,}-?\d{1,}-?\d{1,}|\d{1,}-?\d{1,}-?\d{1,}|\d{1,}|\w{1,}\d+)'  # Handles numbers after #
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

            if not extracted.get('invoice_number'):
                extracted['invoice_number'] = "Unknown Invoice Number"

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
            doc_no_pattern = r"DOCUMENT\s*NO\.\s*BEL\s*\n([A-Z0-9]+)\s+(\d+)"
            doc_no_match = re.search(doc_no_pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            
            if doc_no_match:
                # Extract the document number and assign it to the invoice_number field
                extracted['invoice_number'] = doc_no_match.group(2)
                print("Document No. (as invoice_number):", extracted['invoice_number'])
            else:
                print("Document No. not found, invoice_number not set.")
                    
            for field, pattern in patterns.items():
                print(f"\nTrying to match {field} with pattern: {pattern}")
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL )
                
                if match:
                    extracted[field] = match.group(1)
                    
                    # Check if the match came from "Receipt" keyword
                    if field == "invoice_number":
                        receipt_match = re.search(r'(Receipt number|Receipt |Order)', text, re.IGNORECASE)
                        
                        if receipt_match and not extracted[field].startswith("#"):
                            extracted[field] = f"#{extracted[field]}"
                    
                    print(f"Found match for {field}: {extracted[field]}")
                else:
                    print(f"No match found for {field}")
            
            return extracted

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

    def standardize_date(self, date_str: str, format_type: str) -> Optional[str]:
        """Convert date to ISO format based on detected format."""
        if format_type == 'belgian':
            match = re.match(r'(\d{2})[-/](\d{2})[-/](\d{4})', date_str)
            if match:
                day, month, year = match.groups()
                return f"{year}-{month}-{day}"
        else:
            try:
                date_obj = parse(date_str)
                return date_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError) as e:
                print(f"Failed to parse date: {e}")
                return None
        return None