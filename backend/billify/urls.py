"""
URL configuration for billify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from datetime import datetime
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(*_):
    """
    Provide a helpful overview of the Billify API when accessing the root URL.
    This endpoint serves as both documentation and a health check.

    Note:
        This view ignores all incoming request parameters as it simply returns
        static API information.

    Returns:
        JsonResponse: API information and available endpoints
    """
    api_info = {
        'name': 'Billify API',
        'version': '1.0.0',
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),

        'endpoints': {
            'invoices': {
                'url': '/api/invoices/',
                'methods': ['GET', 'POST'],
                'description': 'Invoice management and processing'
            },
            'cash_flow': {
                'url': '/api/cash-flow/',
                'methods': ['GET'],
                'description': 'Cash flow analytics and projections'
            },
            'accounts': {
                'url': '/api/accounts/',
                'methods': ['GET', 'POST'],
                'description': 'User account management'
            },
            'admin': {
                'url': '/admin/',
                'description': 'Administrative interface (staff only)'
            }
        },

        'documentation': {
            'repository': 'https://github.com/Billify-VOF/billify-prototype',
            'api_docs': '/api/docs/'
        },

        'environment': 'development'
    }

    return JsonResponse(
        api_info,
        json_dumps_params={'indent': 2},
        status=200
    )


urlpatterns = [
    path("", api_root, name='api-root'),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
