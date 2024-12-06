"""API views for invoice management including file uploads."""

from logging import getLogger

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from api.serializers import InvoiceUploadSerializer
from domain.services.invoice_service import InvoiceService
from domain.exceptions import (
    InvalidInvoiceError,
    StorageError,
    ProcessingError
)
from infrastructure.storage.file_system import FileStorage

logger = getLogger(__name__)


class InvoiceUploadView(APIView):
    """Handle invoice uploads and initiate invoice processing workflow."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice_service = InvoiceService()
        self.storage = FileStorage()

    def post(self, request):
        """
        Process uploaded invoice PDF and initiate invoice creation workflow.

        This endpoint:
        1. Validates the uploaded file
        2. Passes it to the invoice service for processing
        3. Returns the created invoice information
        """
        serializer = InvoiceUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        uploaded_file = serializer.validated_data['file']

        try:
            # Delegate to domain service for business logic
            invoice = self.invoice_service.process_invoice(
                file=uploaded_file,
                storage=self.storage
            )

            return Response({
                'message': 'Invoice processed successfully',
                'invoice_id': invoice['id'],
                'status': invoice['status']
            }, status=201)

        except InvalidInvoiceError as e:
            logger.warning(
                "Invalid invoice upload: %s",
                str(e),
                extra={'user_id': request.user.id}
            )
            return Response({
                'error': 'Invalid invoice format',
                'detail': str(e)
            }, status=400)

        except StorageError as e:
            logger.error(
                "Storage error during invoice upload: %s",
                str(e),
                extra={'user_id': request.user.id}
            )
            return Response({
                'error': 'Unable to store invoice',
                'detail': 'Please try again later'
            }, status=503)

        except ProcessingError as e:
            logger.error(
                "Processing error during invoice upload: %s",
                str(e),
                extra={'user_id': request.user.id}
            )
            return Response({
                'error': 'Unable to process invoice',
                'detail': str(e)
            }, status=422)
