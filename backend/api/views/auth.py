from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from application.services.authentication_service import AuthenticationService
from domain.services.authentication_service import (
    AuthenticationService as DomainAuthService,
)
from infrastructure.django.repositories.account_repository import (
    DjangoAccountRepository,
)
from api.serializers import RegisterSerializer

# Dependency Injection
account_repository = DjangoAccountRepository()
domain_auth_service = DomainAuthService(account_repository)
auth_service = AuthenticationService(domain_auth_service)


class RegisterView(APIView):
    """
    API View for handling user registration.

    This view accepts POST requests with user registration data including email,
    username, password and optional company information. It validates the input
    using RegisterSerializer and delegates the registration process to the
    authentication service.

    Methods:
        post(request: Request) -> Response: Handle user registration requests
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        success, response_data = auth_service.register(
            email=serializer.validated_data["email"],
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
            company_name=serializer.validated_data["company_name"],
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED if success else status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"error": "Email/Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, response_data = auth_service.login(identifier, password)

        return Response(
            response_data,
            status=status.HTTP_200_OK if success else status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        success = auth_service.logout(request.user.id)
        return Response(
            {"message": "Successfully logged out." if success else "Logout failed."},
            status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get the current user's profile information.

    Returns:
        Response: User profile data including:
            - id: User ID
            - username: Username
            - email: Email address (optional)
            - firstName: First name (optional)
            - lastName: Last name (optional)
    """
    success, response = auth_service.get_current_user(request.user.id)

    if not success:
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)

    return Response(response)
