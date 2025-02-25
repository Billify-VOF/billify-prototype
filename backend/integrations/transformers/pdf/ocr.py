"""OCR (Optical Character Recognition) service for invoice processing.

This service is responsible for the first step in the PDF processing pipeline:
converting the visual content of PDF documents into machine-readable text.
"""

from pathlib import Path
import pytesseract  # type: ignore
from pdf2image import convert_from_path
import pdfplumber
from logging import getLogger

# Module-level logger
logger = getLogger(__name__)


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
            logger.info("Starting text extraction from %s", pdf_path)
            # First, convert the PDF into a list of images
            # Each image represents one page of the PDF
            pages = convert_from_path(pdf_path)
            logger.info("Extracted %d pages from %s", len(pages), pdf_path)

            # Process each page and collect the extracted text
            text_content = []
            for i, page in enumerate(pages):
                # Use OCR to extract text from the page image
                text = pytesseract.image_to_string(page)
                logger.debug("Extracted text from page %d:", i + 1)
                logger.debug(text)
                text_content.append(text)

            # Combine all pages into a single text document
            return '\n'.join(text_content)

        except Exception as e:
            # If anything goes wrong, wrap the error in our custom error type
            logger.error("Failed to extract text from PDF: %s", str(e))
            raise OCRError(f"Failed to extract text from PDF: {str(e)}") from e

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from a PDF file using pdfplumber."""
        logger.info("Extracting text from PDF using pdfplumber: %s", pdf_path)
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
