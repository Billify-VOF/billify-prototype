"""Core API views for file upload functionality."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from apps.api.serializers import FileUploadSerializer


class FileUploadView(APIView):
    """View for uploading PDF files."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        """Handle PDF file upload, validate and save to temporary storage."""
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            file_path = f'temp/{file.name}'
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return Response(
                {'message': 'File uploaded successfully'}, status=201)
        return Response(serializer.errors, status=400)
