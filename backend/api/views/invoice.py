"""API views for invoice management including file uploads."""

from logging import getLogger
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from api.serializers import InvoiceUploadSerializer
from domain.services.invoice_service import InvoiceService
from application.services.invoice_service import (
    InvoiceProcessingService
)
from domain.exceptions import (
    StorageError,
    ProcessingError
)
from infrastructure.storage.file_system import FileStorage
from infrastructure.django.repositories.invoice_repository import (
    DjangoInvoiceRepository
)
from integrations.transformers.pdf.transformer import PDFTransformer

logger = getLogger(__name__)


class InvoiceUploadView(APIView):
    """Handle invoice uploads and initiate invoice processing workflow."""

    # Authentication is not required during development, for now.
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create repositories
        self.storage_repository = FileStorage()
        self.invoice_repository = DjangoInvoiceRepository()
        # Initialize domain service
        self.invoice_service = InvoiceService()
        # Initialize application service
        self.invoice_processing_service = InvoiceProcessingService(
            invoice_service=self.invoice_service,
            invoice_repository=self.invoice_repository,
            storage_repository=self.storage_repository
        )
        # Initialize transformer for additional data extraction
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
            # Process invoice using the application service
            # This handles file storage, PDF transformation, and invoice
            # creation/update
            result = self.invoice_processing_service.process_invoice(
                file=uploaded_file,
                user_id=self._get_user_id(request)
            )
            logger.info("Invoice processed: %s", result)

            # Prepare response
            due_date = result.get('due_date')
            formatted_date = self._format_date(due_date)

            response_data = {
                'status': 'success',
                'message': 'Invoice processed successfully',
                'invoice': {
                    'id': result['invoice_id'],
                    'status': (
                        str(result.get('status').value)
                        if (result.get('status') and
                            hasattr(result.get('status'), 'value'))
                        else str(result.get('status', ''))
                    ),
                    'file_path': result['file_path'],
                    'updated': result.get('updated', False)
                },
                'invoice_data': {
                    'invoice_number': result.get('invoice_number'),
                    'amount': (
                        str(result.get('amount'))
                        if result.get('amount') is not None
                        else None
                    ),
                    'date': formatted_date,
                    'supplier_name': result.get('supplier_name', ''),
                    'urgency': result.get('urgency')
                }
            }

            logger.info(
                "Successfully processed invoice with extracted data",
                extra={
                    'user_id': self._get_user_id(request),
                    'invoice_id': result['invoice_id'],
                    'has_invoice_number': 'invoice_number' in result,
                    'has_amount': 'amount' in result,
                    'has_date': 'due_date' in result
                }
            )

            return Response(response_data, status=201)

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
            error_msg = str(e)
            logger.error(
                "Processing error during invoice upload: %s",
                error_msg,
                extra={'user_id': self._get_user_id(request)}
            )

            # Check for specific error types embedded in the message
            if "PDF_TRANSFORMATION_ERROR" in error_msg:
                return Response({
                    'status': 'error',
                    'error': 'Unable to extract data from invoice',
                    'detail': error_msg.replace(
                        "PDF_TRANSFORMATION_ERROR: ", ""
                    )
                }, status=422)
            else:
                return Response({
                    'status': 'error',
                    'error': 'Unable to process invoice',
                    'detail': error_msg
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

        # If it's already a date object, use it directly
        if isinstance(raw_due_date, date):
            due_date = raw_due_date
        else:
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

        # Validate due_date format with debug logging
        raw_due_date = data.get('due_date')
        if raw_due_date:
            logger.debug(
                "Validating due_date: %s (type: %s)",
                raw_due_date,
                type(raw_due_date)
            )
            # If it's already a date object, it's valid
            if isinstance(raw_due_date, date):
                logger.debug(
                    "Due date is already a date object: %s",
                    raw_due_date
                )
            else:
                try:
                    # Try multiple date formats for string dates
                    for fmt in ['%Y-%m-%d', '%b %d %Y']:
                        try:
                            logger.debug("Trying format: %s", fmt)
                            parsed_date = datetime.strptime(raw_due_date, fmt)
                            logger.debug(
                                "Successfully parsed date: %s",
                                parsed_date
                            )
                            break  # If any format works, we're good
                        except ValueError as e:
                            logger.debug(
                                "Failed with format %s: %s",
                                fmt,
                                str(e)
                            )
                            continue
                    else:  # No format worked
                        errors.append(f"Invalid date format: {raw_due_date}")
                except (ValueError, TypeError, AttributeError) as e:
                    logger.debug("Date validation error: %s", str(e))
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
        # If it's already a date object, return it
        if isinstance(raw_date, date):
            return raw_date

        # Otherwise try to parse the string
        for fmt in ['%Y-%m-%d', '%b %d %Y']:
            try:
                normalized_date = datetime.strptime(raw_date, fmt)
                logger.debug(
                    "Normalized date %s to %s using format %s",
                    raw_date,
                    normalized_date,
                    fmt
                )
                return normalized_date.date()  # Convert to date object
            except ValueError:
                logger.warning(
                    "Failed to normalize date %s with format %s",
                    raw_date,
                    fmt
                )
                continue

        return None

    def _format_date(self, date_value):
        """Format date in a consistent format.

        Formats the date as 'MMM DD YYYY' if provided, else returns None.
        Frontend expects this specific format to parse correctly.
        """
        if not date_value:
            return None

        # Convert to string if it's a date object
        if isinstance(date_value, (date, datetime)):
            return date_value.strftime('%b %d %Y')

        # If it's already a string, return as is
        return str(date_value)


class InvoicePreviewView(APIView):
    """Handle serving PDF files for preview."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage_repository = FileStorage()

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
            full_path = self.storage_repository.get_file_path(file_path)
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
