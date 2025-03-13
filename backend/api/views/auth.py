from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
import re

User = get_user_model()  # Get the user model dynamically

class LoginView(APIView):
    """
    API endpoint for user login using email or username.
    - Accepts `email` or `username` and `password` as input.
    - Returns a Bearer token if credentials are valid.
    """
    permission_classes = [AllowAny]  # Allow anyone to attempt login

    def post(self, request):
        identifier = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        # Validate input fields
        if not identifier or not password:
            return Response(
                {"error": "Email/Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the input is an email (basic regex check)
        if re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
            try:
                user = User.objects.get(email=identifier)
                username = user.username  # Retrieve the username for authentication
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            username = identifier  # Treat as a username

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate or retrieve existing authentication token
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
    """
    API endpoint for user logout.
    - Requires authentication (user must be logged in).
    - Deletes the user's authentication token to log them out.
    """
    permission_classes = [IsAuthenticated]  # User must be logged in

    def post(self, request):
        # Delete the authentication token (log out user)
        request.auth.delete()
        return Response(
            {"message": "Successfully logged out."},
            status=status.HTTP_200_OK
        )
