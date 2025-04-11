"""API views for invoice management including file uploads."""

from logging import getLogger
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, Optional, List, Union
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from django.urls import resolve

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
# PermissionDenied import needed when authentication code is uncommented for production
# from rest_framework.exceptions import PermissionDenied
from django.db import transaction

from api.serializers import InvoiceUploadSerializer, InvoiceConfirmationSerializer, InvoiceSerializer
from domain.services.invoice_service import InvoiceService
from application.services.invoice_service import InvoiceProcessingService
from domain.exceptions import StorageError, ProcessingError
from infrastructure.storage.file_system import FileStorage
from infrastructure.django.repositories.invoice_repository import (
    DjangoInvoiceRepository,
)
from infrastructure.django.models.invoice import Invoice as DjangoInvoice  # Import the Django model
from infrastructure.django.models.invoice import Invoice

from integrations.transformers.pdf.transformer import PDFTransformer
from django_filters.rest_framework import DjangoFilterBackend

logger = getLogger(__name__)


class BaseInvoiceView(APIView):
    """Base class for invoice-related views with common functionality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize common repositories and services for invoice-related views.

        Sets up the storage repository, invoice repository, and services
        needed by all invoice-related views.

        Args:
            *args: Variable length argument list passed to parent constructor
            **kwargs: Arbitrary keyword arguments passed to parent constructor
        """
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
            storage_repository=self.storage_repository,
        )

    def _get_user_id(self, request: Any) -> int:
        """
        Get the current user ID or default to system user for development.

        DEVELOPMENT MODE ONLY: Currently allowing unauthenticated requests with a default
        user ID for easier testing and development. This should be replaced with proper
        authentication checks before production deployment.

        Args:
            request: Django request object containing authentication info

        Returns:
            int: The authenticated user's ID or 1 if not authenticated (dev only)

        Raises:
            PermissionDenied: If the user is not authenticated (when in production mode)
        """
        # TEMPORARY: Allow unauthenticated requests during development
        if not request.user.is_authenticated:
            logger.warning(
                "DEV MODE: Unauthenticated request allowed with default user ID 1. "
                "This should be secured before production deployment."
            )
            return 1  # Default user ID for development

        # PRODUCTION CODE (uncomment when ready for production):
        # if not request.user.is_authenticated:
        #     raise PermissionDenied("Authentication is required.")

        return request.user.id

    def _get_formatted_status(self, status: Any) -> str:
        """
        Extract and format status value safely.

        Handles different status representations including enum values, strings,
        and None values, ensuring a consistent string output.

        Args:
            status: The status value to format, may be an enum, string or None

        Returns:
            str: Formatted status string
        """
        return str(status.value) if status is not None and hasattr(status, "value") else str(status or "")


class InvoiceUploadView(BaseInvoiceView):
    """Handle invoice uploads and initiate invoice processing workflow."""

    # Authentication is not required during development, for now.
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize with base dependencies and the PDF transformer.

        Args:
            *args: Variable length argument list passed to parent constructor
            **kwargs: Arbitrary keyword arguments passed to parent constructor
        """
        super().__init__(*args, **kwargs)
        # Initialize transformer for additional data extraction
        self.transformer = PDFTransformer()

    def post(self, request: Request) -> Response:
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
        logger.debug("Received file: %s", request.FILES.get("file"))
        serializer = InvoiceUploadSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Serializer errors: %s", serializer.errors)
            return Response(serializer.errors, status=400)

        uploaded_file = serializer.validated_data["file"]
        logger.info("Validated file: %s, size: %s", uploaded_file.name, uploaded_file.size)

        try:
            # Process invoice using the application service
            # This handles file storage, PDF transformation, and invoice
            # creation/update
            result = self.invoice_processing_service.process_invoice(
                file=uploaded_file, user_id=self._get_user_id(request)
            )
            logger.info("Invoice processed: %s", result)

            # Prepare response
            due_date = result.get("due_date")
            formatted_date = self._format_date(due_date)

            # Get status safely
            status = result.get("status")
            status_value = self._get_formatted_status(status)

            response_data = {
                "status": "success",
                "message": "Invoice processed successfully",
                "invoice": {
                    "id": result["invoice_id"],
                    "status": status_value,
                    "file_path": result["file_path"],
                    "updated": result.get("updated", False),
                },
                "invoice_data": {
                    "invoice_number": result.get("invoice_number"),
                    "amount": (str(result.get("amount")) if result.get("amount") is not None else None),
                    "date": formatted_date,
                    "supplier_name": result.get("supplier_name", ""),
                    "urgency": result.get(
                        "urgency",
                        {
                            "level": None,
                            "display_name": "",
                            "color_code": None,
                            "is_manual": False,
                        },
                    ),
                },
            }

            logger.info(
                "Successfully processed invoice with extracted data",
                extra={
                    "user_id": self._get_user_id(request),
                    "invoice_id": result["invoice_id"],
                    "has_invoice_number": "invoice_number" in result,
                    "has_amount": "amount" in result,
                    "has_date": "due_date" in result,
                },
            )

            return Response(response_data, status=201)

        except StorageError as e:
            logger.error(
                "Storage error during invoice upload: %s",
                str(e),
                extra={"user_id": self._get_user_id(request)},
            )
            return Response(
                {
                    "status": "error",
                    "error": "Unable to store invoice",
                    "detail": "Please try again later",
                },
                status=503,
            )

        except ProcessingError as e:
            error_msg = str(e)
            logger.error(
                "Processing error during invoice upload: %s",
                error_msg,
                extra={"user_id": self._get_user_id(request)},
            )

            # Check for specific error types embedded in the message
            if "PDF_TRANSFORMATION_ERROR" in error_msg:
                return Response(
                    {
                        "status": "error",
                        "error": "Unable to extract data from invoice",
                        "detail": error_msg.replace("PDF_TRANSFORMATION_ERROR: ", ""),
                    },
                    status=422,
                )
            else:
                return Response(
                    {
                        "status": "error",
                        "error": "Unable to process invoice",
                        "detail": error_msg,
                    },
                    status=422,
                )

        except KeyError as e:
            logger.error("Missing required data: %s", e)
            return Response({"error": "Missing required data", "details": str(e)}, status=400)

        except (ValueError, TypeError, OSError) as e:
            logger.exception(
                "Unexpected error occurred during invoice upload",
                extra={"user_id": self._get_user_id(request)},
            )
            return Response({"error": "Internal server error", "details": str(e)}, status=500)

    def _convert_amount(self, amount_str: Optional[str]) -> Optional[Decimal]:
        """Convert string amount to Decimal or None."""
        return Decimal(amount_str) if amount_str else None

    def process_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process extracted data and convert due_date to datetime object."""
        self.validate_extracted_data(extracted_data)
        raw_due_date = extracted_data.get("due_date")

        # If it's already a date object, use it directly
        if isinstance(raw_due_date, date):
            due_date: Optional[date] = raw_due_date
        else:
            due_date = self.normalize_date(raw_due_date) if raw_due_date else None

        processed_data = {
            "invoice_number": extracted_data.get("invoice_number"),
            "amount": self._convert_amount(extracted_data.get("amount")),
            "due_date": due_date,
            "supplier_name": extracted_data.get("supplier_name"),
        }
        return processed_data

    def validate_extracted_data(self, data: Dict[str, Any]) -> None:
        """Validate extracted data to ensure correct format."""
        errors: List[str] = []

        # Validate invoice number
        if not data.get("invoice_number"):
            errors.append("Invoice number is missing.")

        # Validate due_date format with debug logging
        raw_due_date = data.get("due_date")
        if raw_due_date:
            logger.debug("Validating due_date: %s (type: %s)", raw_due_date, type(raw_due_date))
            # If it's already a date object, it's valid
            if isinstance(raw_due_date, date):
                logger.debug("Due date is already a date object: %s", raw_due_date)
            else:
                try:
                    # Try multiple date formats for string dates
                    for fmt in ["%Y-%m-%d", "%b %d %Y"]:
                        try:
                            logger.debug("Trying format: %s", fmt)
                            parsed_date = datetime.strptime(raw_due_date, fmt)
                            logger.debug("Successfully parsed date: %s", parsed_date)
                            break  # If any format works, we're good
                        except ValueError as e:
                            logger.debug("Failed with format %s: %s", fmt, str(e))
                            continue
                    else:  # No format worked
                        errors.append(f"Invalid date format: {raw_due_date}")
                except (ValueError, TypeError, AttributeError) as e:
                    logger.debug("Date validation error: %s", str(e))
                    errors.append(f"Invalid date format: {raw_due_date}")

        # Validate amount
        try:
            if data.get("amount"):
                Decimal(data["amount"])
        except (ValueError, TypeError):
            errors.append(f"Invalid amount: {data.get('amount')}")

        if errors:
            logger.error("Validation errors: %s", errors)
            raise ValueError(errors)

    def normalize_date(self, raw_date: Optional[str]) -> Optional[date]:
        """Normalize the date format for consistent internal representation."""
        # If it's already a date object, return it
        if isinstance(raw_date, date):
            return raw_date

        # Early return if raw_date is None
        if raw_date is None:
            return None

        # Otherwise try to parse the string
        for fmt in ["%Y-%m-%d", "%b %d %Y"]:
            try:
                normalized_date = datetime.strptime(raw_date, fmt)
                logger.debug(
                    "Normalized date %s to %s using format %s",
                    raw_date,
                    normalized_date,
                    fmt,
                )
                return normalized_date.date()  # Convert to date object
            except ValueError:
                logger.warning("Failed to normalize date %s with format %s", raw_date, fmt)
                continue

        return None

    def _format_date(self, date_value: Optional[Union[date, datetime, str]]) -> Optional[str]:
        """Format date in a consistent format.

        Formats the date as 'MMM DD YYYY' if provided, else returns None.
        Frontend expects this specific format to parse correctly.
        """
        if not date_value:
            return None

        # Convert to string if it's a date object
        if isinstance(date_value, (date, datetime)):
            return date_value.strftime("%b %d %Y")

        # If it's already a string, return as is
        return str(date_value)


class InvoicePreviewView(BaseInvoiceView):
    """Handle serving PDF files for preview."""

    def get(self, _: Any, file_path: str) -> Union[FileResponse, Response]:
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
                return Response({"error": "File not found"}, status=404)

            logger.info("File exists, attempting to serve: %s", full_path)
            response = FileResponse(open(full_path, "rb"), content_type="application/pdf")
            filename = Path(file_path).name
            response["Content-Disposition"] = f'inline; filename="{filename}"'
            logger.info("Successfully created response for file: %s", filename)
            return response

        except (OSError, StorageError, ValueError) as e:
            logger.exception("Error serving PDF file: %s", str(e))
            return Response({"error": "Failed to serve file", "detail": str(e)}, status=500)


class InvoiceConfirmationView(BaseInvoiceView):
    """
    API endpoint for finalizing invoice processing and storage.

    This view handles the second phase of the two-phase invoice processing workflow:
    1. First phase: Invoice upload and temporary storage (handled by InvoiceUploadView)
    2. Second phase: Invoice confirmation and permanent storage (handled by this view)

    The view provides an endpoint that accepts invoice confirmation requests,
    transfers files from temporary to permanent storage, and updates invoice
    records with finalized data including urgency levels.

    URLs:
        POST /api/invoices/{invoice_id}/confirm/ - Finalize an invoice
    """

    # Authentication is not required during development, for now.
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Finalize an invoice by transferring it from temporary to permanent storage.

        This endpoint completes the invoice processing workflow by:
        1. Validating the invoice data through the serializer
        2. Setting the optional urgency level if provided
        3. Transferring the file from temporary to permanent storage
        4. Updating the invoice record with the final storage path
        5. Returning detailed invoice information for frontend display

        Args:
            request: Django HTTP request object containing confirmation data
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response: JSON response with finalized invoice data or error details

        HTTP Status Codes:
            200 OK: Invoice successfully finalized
            400 Bad Request: Invalid input data
            404 Not Found: Invoice with the specified ID does not exist
            422 Unprocessable Entity: Business rule violations
            503 Service Unavailable: Storage service errors
            500 Internal Server Error: Unexpected errors
        """
        # Extract invoice_id from the URL kwargs
        invoice_id = kwargs.get("invoice_id")
        if not invoice_id:
            logger.error("Invoice ID is missing in the URL.")
            return Response({"error": "Invoice ID is required."}, status=400)

        serializer = InvoiceConfirmationSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Serializer errors: %s", serializer.errors)
            return Response(serializer.errors, status=400)

        # Check if invoice exists before proceeding
        try:
            # Try to get the invoice to verify it exists
            print(f"Invoice ID: {invoice_id}")
            self.invoice_repository.get_by_id(invoice_id)
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(
                "Invalid invoice ID or invoice not found",
                extra={"invoice_id": invoice_id, "user_id": self._get_user_id(request), "error": str(e)},
            )
            return Response({"error": "Invoice not found."}, status=404)
        except Exception as e:
            logger.error(
                "Error when checking invoice existence",
                extra={"invoice_id": invoice_id, "user_id": self._get_user_id(request), "error": str(e)},
            )
            return Response({"error": "Failed to verify invoice existence."}, status=500)

        try:

            # Extract validated data
            temp_file_path = serializer["temp_file_path"]
            urgency_level = serializer.validated_data.get("urgency_level")

            # Check if the temporary file exists
            # Validate that the path is within the temporary storage area
            # if not temp_file_path.startswith("temp/"):
            #     logger.error("Invalid temporary file path: %s", temp_file_path)
            #     return Response({"error": "Invalid temporary file path."}, status=400)
            full_temp_path = self.storage_repository.get_file_path(temp_file_path.value)
            if not Path(full_temp_path).exists():
                logger.error("Temporary file not found at path: %s", full_temp_path)
                return Response({"error": "Temporary file not found."}, status=404)

            # Wrap the finalization process in a transaction to ensure atomicity
            with transaction.atomic():
                try:
                    # Finalize the invoice using the application service
                    result = self.invoice_processing_service.finalize_invoice(
                        invoice_id=invoice_id,
                        temp_file_path=full_temp_path,
                        urgency_level=urgency_level,
                        user_id=self._get_user_id(request),
                        invoice_data = request.data
                    )


                    # Get status safely
                    status_value = self._get_formatted_status(result.get("status"))

                    # Prepare response
                    response_data = {
                        "status": "success",
                        "message": "Invoice finalized successfully",
                        "invoice": {
                            "id": result["invoice_id"],
                            "invoice_number": result["invoice_number"],
                            "status": status_value,
                            "file_path": result["file_path"],
                            "finalized": True,
                        },
                        "urgency": result.get("urgency"),
                        "timestamps": result.get("timestamps", {}),
                    }

                    logger.info(
                        "Successfully finalized invoice",
                        extra={
                            "user_id": self._get_user_id(request),
                            "invoice_id": result["invoice_id"],
                        },
                    )

                    return Response(response_data, status=200)

                except StorageError as e:
                    # Transaction will be rolled back
                    logger.error(
                        "Storage error during invoice finalization: %s",
                        str(e),
                        extra={"user_id": self._get_user_id(request), "invoice_id": invoice_id},
                    )
                    return Response(
                        {
                            "status": "error",
                            "error": "Unable to store invoice",
                            "detail": "Please try again later",
                        },
                        status=503,
                    )

                except ProcessingError as e:
                    # Transaction will be rolled back
                    error_msg = str(e)
                    logger.error(
                        "Processing error during invoice finalization: %s",
                        error_msg,
                        extra={"user_id": self._get_user_id(request), "invoice_id": invoice_id},
                    )

                    return Response(
                        {
                            "status": "error",
                            "error": "Unable to finalize invoice",
                            "detail": error_msg,
                        },
                        status=422,
                    )

        except (ValueError, TypeError, OSError) as e:
            # Catch any other errors outside the transaction
            logger.exception(
                "Unexpected error occurred during invoice finalization",
                extra={"user_id": self._get_user_id(request), "invoice_id": invoice_id},
            )
            return Response({"error": "Internal server error", "details": str(e)}, status=500)


class InvoiceViewSet(ModelViewSet):
    """
    A viewset for viewing and editing invoice instances.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'due_date']
