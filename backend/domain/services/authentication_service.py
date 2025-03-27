from typing import Optional, Tuple
from domain.models.account import Account
from domain.repositories.interfaces.account_repository import AccountRepository


class AuthenticationService:
    """Domain service for authentication operations."""

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def login(
        self, identifier: str, password: str
    ) -> Tuple[bool, Optional[Account], str]:
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

        authenticated_account = self.account_repository.authenticate(
            account.username, password
        )

        if not authenticated_account:
            return False, None, "Invalid credentials"

        return True, authenticated_account, ""

    def logout(self, account_id: int) -> bool:
        """Log out a user."""
        account = self.account_repository.find_by_id(account_id)
        return account is not None
