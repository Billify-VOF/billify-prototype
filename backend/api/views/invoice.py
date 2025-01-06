"""API views for invoice management including file uploads."""

from logging import getLogger
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from api.serializers import InvoiceUploadSerializer
from domain.services.invoice_service import InvoiceService
from domain.exceptions import (
    InvalidInvoiceError,
    StorageError,
    ProcessingError
)
from integrations.transformers.pdf.transformer import PDFTransformer
from infrastructure.storage.file_system import FileStorage

logger = getLogger(__name__)


class InvoiceUploadView(APIView):
    """Handle invoice uploads and initiate invoice processing workflow."""

    # Authentication is not required during development, for now.
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice_service = InvoiceService()
        self.storage = FileStorage()
        # Add the PDF transformer as a class dependency
        self.transformer = PDFTransformer()

    def _get_user_id(self, request):
        """Get the current user ID or default to 1."""
        return request.user.id if request.user.is_authenticated else 1

    def post(self, request):
        """
        Process uploaded invoice PDF and initiate invoice creation workflow.

        This endpoint performs a complete processing pipeline:
        1. Validates the uploaded file
        2. Stores the file securely
        3. Extracts data using OCR and text analysis
        4. Creates an invoice record with the extracted data
        5. Returns both the invoice record and extracted information
        """

        logger.debug("Request data: %s", request.data)
        logger.debug("Received file: %s", request.FILES.get('file'))
        serializer = InvoiceUploadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Serializer errors: %s", serializer.errors)
            return Response(serializer.errors, status=400)

        uploaded_file = serializer.validated_data['file']
        logger.info(
            "Validated file: %s, size: %s",
            uploaded_file.name,
            uploaded_file.size
        )

        try:
            # First, let invoice service handle storage and basic processing
            invoice = self.invoice_service.process_invoice(
                file=uploaded_file,
                storage=self.storage,
                user_id=self._get_user_id(request)
            )
            logger.info("Invoice processed: %s", invoice)

            if 'file_path' not in invoice:
                raise ProcessingError(
                    "Missing file path in processed invoice"
                )

            # Now, process the stored PDF to extract structured data
            file_path = self.storage.get_file_path(invoice['file_path'])
            logger.info("File path: %s", file_path)
            extracted_data = self.transformer.transform(Path(file_path))
            logger.info("Extracted data: %s", extracted_data)

            # Process extracted data
            processed_data = self.process_extracted_data(extracted_data)
            logger.info("Processed data: %s", processed_data)

            # Combine invoice record with extracted data in response
            response_data = {
                'status': 'success',
                'message': 'Invoice processed successfully',
                'invoice': {
                    'id': invoice['invoice_id'],
                    'status': invoice['status'],
                    'file_path': invoice['file_path'],
                    'updated': invoice.get('updated', False)
                },
                'invoice_data': {
                    'invoice_number': processed_data.get('invoice_number'),
                    'amount': str(processed_data.get('amount')),
                    'date': self._format_date(processed_data.get('due_date')),
                    'supplier_name': processed_data.get('supplier_name')
                }
            }

            logger.info(
                "Successfully processed invoice with extracted data",
                extra={
                    'user_id': self._get_user_id(request),
                    'invoice_id': invoice['invoice_id'],
                    'has_invoice_number': bool(
                        processed_data.get('invoice_number')),
                    'has_amount': bool(processed_data.get('amount')),
                    'has_date': bool(processed_data.get('due_date'))
                }
            )

            return Response(response_data, status=201)

        except InvalidInvoiceError as e:
            logger.warning(
                "Invalid invoice upload: %s",
                str(e),
                extra={'user_id': self._get_user_id(request)}
            )
            return Response({
                'status': 'error',
                'error': 'Invalid invoice format',
                'detail': str(e)
            }, status=400)

        except StorageError as e:
            logger.error(
                "Storage error during invoice upload: %s",
                str(e),
                extra={'user_id': self._get_user_id(request)}
            )
            return Response({
                'status': 'error',
                'error': 'Unable to store invoice',
                'detail': 'Please try again later'
            }, status=503)

        except ProcessingError as e:
            logger.error(
                "Processing error during invoice upload: %s",
                str(e),
                extra={'user_id': self._get_user_id(request)}
            )
            return Response({
                'status': 'error',
                'error': 'Unable to process invoice',
                'detail': str(e)
            }, status=422)

        except KeyError as e:
            logger.error("Missing required data: %s", e)
            return Response(
                {'error': 'Missing required data', 'details': str(e)},
                status=400
            )

        except (ValueError, TypeError, OSError) as e:
            logger.exception(
                "Unexpected error occurred during invoice upload",
                extra={'user_id': self._get_user_id(request)}
            )
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=500
            )

    def _convert_amount(self, amount_str):
        """Convert string amount to Decimal or None."""
        return Decimal(amount_str) if amount_str else None

    def process_extracted_data(self, extracted_data):
        """Process extracted data and convert due_date to datetime object."""
        self.validate_extracted_data(extracted_data)
        raw_due_date = extracted_data.get('due_date')
        due_date = (
            self.normalize_date(raw_due_date) if raw_due_date else None
        )

        processed_data = {
            'invoice_number': extracted_data.get('invoice_number'),
            'amount': self._convert_amount(
                extracted_data.get('amount')
            ),
            'due_date': due_date,
            'supplier_name': extracted_data.get('supplier_name'),
        }
        return processed_data

    def validate_extracted_data(self, data):
        """Validate extracted data to ensure correct format."""
        errors = []

        # Validate invoice number
        if not data.get('invoice_number'):
            errors.append("Invoice number is missing.")

        # Validate due_date format
        raw_due_date = data.get('due_date')
        if raw_due_date:
            try:
                # Try multiple date formats
                for fmt in ['%Y-%m-%d', '%b %d %Y']:
                    try:
                        datetime.strptime(raw_due_date, fmt)
                        break  # If any format works, we're good
                    except ValueError:
                        continue
                else:  # No format worked
                    errors.append(f"Invalid date format: {raw_due_date}")
            except (ValueError, TypeError, AttributeError):
                errors.append(f"Invalid date format: {raw_due_date}")

        # Validate amount
        try:
            if data.get('amount'):
                Decimal(data['amount'])
        except (ValueError, TypeError):
            errors.append(f"Invalid amount: {data.get('amount')}")

        if errors:
            logger.error("Validation errors: %s", errors)
            raise ValueError(errors)

    def normalize_date(self, raw_date):
        """Normalize the date format for consistent internal representation."""
        for fmt in ['%Y-%m-%d', '%b %d %Y']:
            try:
                normalized_date = datetime.strptime(raw_date, fmt)
                logger.debug(
                    "Normalized date %s to %s using format %s",
                    raw_date,
                    normalized_date,
                    fmt
                )
                return normalized_date
            except ValueError:
                continue
        logger.warning("Failed to normalize date: %s", raw_date)
        return None

    def _format_date(self, date):
        """Format date in a consistent format."""
        return date.strftime('%b %d %Y') if date else None


class InvoicePreviewView(APIView):
    """Handle serving PDF files for preview."""

    def get(self, _, file_path):
        """
        Serve a PDF file for preview.

        Args:
            file_path: The relative path to the PDF file

        Returns:
            FileResponse: The PDF file
        """
        logger.info("Preview requested for file: %s", file_path)
        try:
            storage = FileStorage()
            full_path = storage.get_file_path(file_path)
            logger.info("Full path resolved to: %s", full_path)

            if not Path(full_path).exists():
                logger.error("File not found at path: %s", full_path)
                return Response(
                    {'error': 'File not found'},
                    status=404
                )

            logger.info("File exists, attempting to serve: %s", full_path)
            response = FileResponse(
                open(full_path, 'rb'),
                content_type='application/pdf'
            )
            filename = Path(file_path).name
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            logger.info("Successfully created response for file: %s", filename)
            return response

        except (OSError, StorageError, ValueError) as e:
            logger.exception("Error serving PDF file: %s", str(e))
            return Response(
                {'error': 'Failed to serve file', 'detail': str(e)},
                status=500
            )
