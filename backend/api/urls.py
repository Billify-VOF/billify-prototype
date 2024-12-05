"""URL configuration for the API application."""

from django.urls import path
from api.views.invoice import FileUploadView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
