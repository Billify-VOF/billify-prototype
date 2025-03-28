from typing import Tuple, Dict, Any
from rest_framework.authtoken.models import Token
from domain.services.authentication_service import (
    AuthenticationService as DomainAuthService,
)


class AuthenticationService:
    """Application service for authentication operations."""

    def __init__(self, domain_auth_service: DomainAuthService):
        self.domain_auth_service = domain_auth_service

    def register(
        self, email: str, username: str, password: str, company_name: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Register a new user account.

        Args:
            email: User's email address
            username: User's username
            password: User's password
            company_name: User's company name

        Returns:
            Tuple containing:
            - bool: Success status
            - dict: Response data with account info or error message
        """
        success, account, error_message = self.domain_auth_service.register(
            email=email,
            username=username,
            password=password,
            company_name=company_name
        )

        if not success:
            return False, {"error": error_message}

        return True, {
            "message": "Registration successful",
            "user": {
                "id": account.id,
                "username": account.username,
                "email": account.email,
                "company_name": account.company_name
            }
        }

    def login(self, identifier: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        success, account, error_message = self.domain_auth_service.login(identifier, password)

        if not success:
            return False, {"error": error_message}

        token, _ = Token.objects.get_or_create(user_id=account.id)
        return True, {"token": token.key}

    def logout(self, account_id: int) -> bool:
        if not self.domain_auth_service.logout(account_id):
            return False

        try:
            token = Token.objects.get(user_id=account_id)
            token.delete()
            return True
        except Token.DoesNotExist:
            return False
