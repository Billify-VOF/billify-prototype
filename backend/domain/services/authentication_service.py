from typing import Optional, Tuple
import logging
from domain.models.account import Account
from domain.repositories.interfaces.account_repository import AccountRepository
from domain.exceptions import ValidationError, RepositoryError

logger = logging.getLogger(__name__)


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
                Account(id=None, username=username, email=email, password=password, company_name=company_name)
            )
            return True, account, ""
        except ValidationError as e:
            logger.error("Account validation failed during registration: %s", str(e))
            return False, None, "Invalid account data provided"
        except RepositoryError as e:
            logger.error("Database error during account registration: %s", str(e))
            return False, None, "Unable to create account at this time. Please try again later."
        except Exception:
            logger.exception("Unexpected error during account registration")
            return False, None, "An unexpected error occurred. Please try again later."

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

    def get_current_user(self, user_id: int) -> Tuple[bool, Optional[Account], str]:
        """Get the current authenticated user's account information.

        Args:
            user_id: ID of the authenticated user

        Returns:
            Tuple containing:
            - bool: Success status
            - Optional[Account]: User's account if found, None otherwise
            - str: Error message if unsuccessful, empty string otherwise
        """
        try:
            account = self.account_repository.find_by_id(user_id)
            if not account:
                return False, None, "User not found"
            return True, account, ""
        except RepositoryError as e:
            logger.error("Repository error while fetching user profile: %s", str(e))
            return False, None, "Unable to fetch user profile at this time"
        except Exception:
            logger.exception("Unexpected error while fetching user profile")
            return False, None, "An unexpected error occurred"
