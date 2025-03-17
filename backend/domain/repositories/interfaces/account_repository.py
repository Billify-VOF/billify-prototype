from abc import ABC, abstractmethod
from typing import Optional
from domain.models.account import Account


class AccountRepository(ABC):
    """Interface for account repository operations."""

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Account]:
        """Find account by ID."""
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[Account]:
        """Find account by username."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Account]:
        """Find account by email."""
        pass

    @abstractmethod
    def save(self, account: Account) -> Account:
        """Save account (create or update)."""
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[Account]:
        """Authenticate user with username/email and password."""
        pass
