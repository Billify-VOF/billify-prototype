"""Domain model for user accounts.

This module contains the Account domain entity which represents a user account
in the system. It encapsulates the core business rules and validation logic
for user accounts, including authentication requirements and user information.
"""

from typing import Optional


class Account:
    """Domain entity representing a user account in the system.

    This class encapsulates the core business rules and data for user accounts.
    It provides methods for validation and access to user information while
    maintaining proper encapsulation of sensitive data like passwords.
    """

    def __init__(
        self,
        id: Optional[int],
        username: str,
        email: str,
        company_name: Optional[str] = None,
        password: Optional[str] = None,
        is_active: bool = True,
        first_name: str = "",
        last_name: str = "",
    ) -> None:
        """Initialize a new Account instance.

        Args:
            id: Unique identifier for the account. Can be None for new accounts.
            username: Unique username for the account.
            email: User's email address.
            company_name: Name of the user's company. Optional.
            password: User's password. Optional and not stored directly.
            is_active: Whether the account is active. Defaults to True.
            first_name: User's first name. Defaults to empty string.
            last_name: User's last name. Defaults to empty string.

        Raises:
            ValueError: If required fields (email, username) are empty.
        """
        self.id = id
        self.username = username
        self.email = email
        self.company_name = company_name
        self._password = password  # Not stored directly, used for authentication
        self.is_active = is_active
        self.first_name = first_name
        self.last_name = last_name

        # Validate required fields
        if not self.email or not self.username:
            raise ValueError("Email and username are required")

    def is_valid_for_authentication(self) -> bool:
        """Check if the account is valid for authentication.

        An account is considered valid for authentication if:
        1. The account is active
        2. Has a valid email address
        3. Has a valid username

        Returns:
            bool: True if the account is valid for authentication, False otherwise.
        """
        return self.is_active and bool(self.email) and bool(self.username)

    @property
    def full_name(self) -> str:
        """Get the user's full name.

        Returns the user's full name if both first and last names are provided,
        otherwise returns the username as a fallback.

        Returns:
            str: User's full name or username if full name is not available.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
