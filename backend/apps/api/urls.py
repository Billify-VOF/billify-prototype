"""URL configuration for the API application."""

from django.urls import path
from apps.api.views.core import FileUploadView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
