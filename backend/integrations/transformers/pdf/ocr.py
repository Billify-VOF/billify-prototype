"""OCR (Optical Character Recognition) service for invoice processing.

This service is responsible for the first step in the PDF processing pipeline:
converting the visual content of PDF documents into machine-readable text.
"""

from pathlib import Path
import pytesseract
from pdf2image import convert_from_path


class OCRError(Exception):
    """
    Raised when text extraction from a PDF fails.
    We create a specific error type to distinguish OCR failures
    from other types of errors in our system.
    """


class OCRService:
    """
    Handles the extraction of text from PDF documents using OCR technology.

    This service encapsulates all the complexity of converting PDF pages
    to images and then extracting text from those images. It provides a
    simple interface to the rest of our system: give it a PDF, get back text.
    """

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract all text content from a PDF document.

        Args:
            pdf_path: Path to the PDF file we want to process

        Returns:
            A string containing all extracted text from the PDF

        Raises:
            OCRError: If text extraction fails for any reason
        """
        try:
            # First, convert the PDF into a list of images
            # Each image represents one page of the PDF
            pages = convert_from_path(pdf_path)

            # Process each page and collect the extracted text
            text_content = []
            for page in pages:
                # Use OCR to extract text from the page image
                text = pytesseract.image_to_string(page)
                text_content.append(text)

            # Combine all pages into a single text document
            return '\n'.join(text_content)

        except Exception as e:
            # If anything goes wrong, wrap the error in our custom error type
            raise OCRError(f"Failed to extract text from PDF: {str(e)}") from e
