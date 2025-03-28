from typing import Optional, Tuple
from domain.models.account import Account
from domain.repositories.interfaces.account_repository import AccountRepository


class AuthenticationService:
    """Domain service for authentication operations."""

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def register(
        self, email: str, username: str, password: str, company_name: str
    ) -> Tuple[bool, Optional[Account], str]:
        """Register a new user account with the given details.

        Args:
            email: User's email address
            username: User's username
            password: User's password
            company_name: User's company name

        Returns:
            Tuple containing:
            - bool: Success status
            - Optional[Account]: Created account if successful, None otherwise
            - str: Error message if unsuccessful, empty string otherwise
        """
        # Check if email already exists
        if self.account_repository.find_by_email(email):
            return False, None, "Email already exists"

        # Check if username already exists
        if self.account_repository.find_by_username(username):
            return False, None, "Username already exists"

        # Create new account
        try:
            account = self.account_repository.save(
                Account(
                    id=None,
                    username=username,
                    email=email,
                    password=password,
                    company_name=company_name
                )
            )
            return True, account, ""
        except Exception as e:
            return False, None, str(e)

    def login(self, identifier: str, password: str) -> Tuple[bool, Optional[Account], str]:
        """Authenticate a user with identifier (username or email) and password."""
        is_email = "@" in identifier

        # Find account by identifier
        account = (
            self.account_repository.find_by_email(identifier)
            if is_email
            else self.account_repository.find_by_username(identifier)
        )

        if not account:
            return (
                False,
                None,
                f"Account with this {'email' if is_email else 'username'} does not exist",
            )

        if not account.is_valid_for_authentication():
            return False, None, "Account is not active"

        authenticated_account = self.account_repository.authenticate(account.username, password)

        if not authenticated_account:
            return False, None, "Invalid credentials"

        return True, authenticated_account, ""

    def logout(self, account_id: int) -> bool:
        """Log out a user."""
        account = self.account_repository.find_by_id(account_id)
        return account is not None
