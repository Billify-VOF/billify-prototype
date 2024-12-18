"""API views for invoice management including file uploads."""

from logging import getLogger
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
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

        print("Starting upload process")
        print(f"Request data: {request.data}")
        print(f"Received file: {request.FILES.get('file')}")
        serializer = InvoiceUploadSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=400)

        uploaded_file = serializer.validated_data['file']
        print(
            f"Validated file: {uploaded_file.name}, "
            f"size: {uploaded_file.size}"
        )

        try:
            # First, let invoice service handle storage and basic processing
            invoice = self.invoice_service.process_invoice(
                file=uploaded_file,
                storage=self.storage,
                user_id=1  # Hardcode for development
            )
            print(f"Invoice processed: {invoice}")

            if 'file_path' not in invoice:
                raise ProcessingError(
                    "Missing file path in processed invoice"
                )

            # Now, process the stored PDF to extract structured data
            file_path = self.storage.get_file_path(invoice['file_path'])
            print(f"File path: {file_path}")
            extracted_data = self.transformer.transform(Path(file_path))
            print(f"Extracted data: {extracted_data}")

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
                    'invoice_number': extracted_data.get('invoice_number'),
                    'amount': str(extracted_data.get('amount')),
                    'date': extracted_data.get('due_date').strftime('%b %d %Y') if extracted_data.get('due_date') else None,
                    'supplier_name': extracted_data.get('supplier_name')
                }
            }

            logger.info(
                "Successfully processed invoice with extracted data",
                extra={
                    'user_id': 1,  # Hardcode for development
                    'invoice_id': invoice['invoice_id'],
                    'has_invoice_number': bool(
                        extracted_data.get('invoice_number')),
                    'has_amount': bool(extracted_data.get('amount')),
                    'has_date': bool(extracted_data.get('date'))
                }
            )

            return Response(response_data, status=201)

        except InvalidInvoiceError as e:
            logger.warning(
                "Invalid invoice upload: %s",
                str(e),
                extra={'user_id': 1}  # Hardcode for development
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
                extra={'user_id': 1}  # Hardcode for development
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
                extra={'user_id': 1}  # Hardcode for development
            )
            return Response({
                'status': 'error',
                'error': 'Unable to process invoice',
                'detail': str(e)
            }, status=422)
