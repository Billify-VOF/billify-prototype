"""Ponto-related repository interfaces for data access operations.

This module defines the abstract interface for Ponto-Connect operations
using Python's ABC (Abstract Base Class). The interface serves as a contract
that all concrete repository implementations must follow.

Key concepts:
    - ABC (Abstract Base Class): Defines an interface that cannot be
      instantiated directly
    - @abstractmethod: Marks methods that MUST be implemented by any
      concrete repository class
    - Repository Pattern: Separates domain logic from data access
      implementation details

Example:
    # Concrete implementation must implement all abstract methods
    class DjangoIbanityAccountRepository(IbanityAccountRepository):
        def save(
            self, ibanity_account: IbanityAccount, user
        ) -> IbanityAccount:
            # Implementation specific to PostgreSQL
            pass
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple

from domain.models.ponto import IbanityAccount, PontoToken


class IbanityAccountRepository(ABC):
    """Interface defining Ibanity account data access operations.

    This abstract base class serves as a contract for IbanityAccount persistence
    operations. Any concrete implementation (e.g., Django ORM, SQLAlchemy,
    etc.) must implement all methods marked with @abstractmethod.

    The Repository pattern used here:
    1. Separates domain logic from data access details
    2. Makes the system more maintainable and testable
    3. Allows swapping different storage implementations without changing
       domain code
    4. Follows the Dependency Inversion Principle (SOLID)

    Example:
        class DjangoIbanityAccountRepository(IbanityAccountRepository):
            def save(
                self, ibanity_account: IbanityAccount, user
            ) -> IbanityAccount:
                # Implementation specific to PostgreSQL
                pass
    """

    @abstractmethod
    def save(self, ibanity_account: IbanityAccount) -> IbanityAccount:
        """Save an ibanity account to the database.

        This method must either create a new Ibanity account or update
        an existing one based on the user id. It should handle the persistence
        details while maintaining the domain model's integrity.

        Args:
            ibanity_account (IbanityAccount): The domain Ibanity account model
                to persist
            user (User): User instance who uploaded/created the Ibanity account

        Returns:
            IbanityAccount: The persisted domain IbanityAccount model,
                potentially with updated metadata (e.g., ID, timestamps)

        Raises:
            InvalidIbanityAccountError: If the IbanityAccount data is invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_or_create(self, user, account_id: str, data: Dict[str, Any]) -> Tuple[IbanityAccount, bool]:
        """Get an existing account or create a new one.

        Args:
            user: The user who owns the account
            account_id: The Ponto account ID
            data: The account data

        Returns:
            Tuple[IbanityAccount, bool]: The account and whether it was created
        """

    @abstractmethod
    def get_by_id(self, ibanity_account_id: int) -> Optional[IbanityAccount]:
        """Retrieve an IbanityAccount by id.

        Args:
            ibanity_account_id (int): IbanityAccount Model Id

        Returns:
            Optional[IbanityAccount]: The domain IbanityAccount model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_by_user(self, user) -> IbanityAccount:
        """Get an account by user.

        Args:
            user: The user who owns the account

        Returns:
            IbanityAccount: The account data

        Raises:
            IbanityAccountNotFoundError: If no account exists for the user
        """

    @abstractmethod
    def get_by_account_id(self, account_id: str) -> Optional[IbanityAccount]:
        """Retrieve an IbanityAccount by Ibanity account id.

        Args:
            account_id (str): The Ponto-Connect account id.

        Returns:
            Optional[IbanityAccount]: The domain IbanityAccount model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def update(self, ibanity_account: IbanityAccount, user) -> IbanityAccount:
        """Update an existing IbanityAccount.

        This method should update all fields of an existing IbanityAccount
        while maintaining any metadata (e.g., created_at timestamp).

        Args:
            ibanity_account (IbanityAccount): The domain IbanityAccount with
                updated data
            user (User): User instance performing the update

        Returns:
            IbanityAccount: The updated domain IbanityAccount model

        Raises:
            InvalidIbanityAccountError: If the IbanityAccount doesn't exist
                or data is invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def update_by_account_id(self, account_id: str, data: Dict[str, Any]) -> IbanityAccount:
        """Update an existing IbanityAccount.

        This method should update all fields of an existing IbanityAccount
        while maintaining any metadata (e.g., created_at timestamp).

        Args:
            account_id (str): The IbanityAccount account_id
            data (dict): New data or replace data
                - 'description': Description of IbanityAccount
                - 'product': Product
                - 'reference': Reference
                - 'currency': Currency
                - 'authorization_expiration_expected_at': Authorization
                  expiration time
                - 'current_balance': Current balance
                - 'available_balance': Available balance
                - 'subtype': Subtype
                - 'holder_name': Holder name
                - 'resource_id': Resource ID

        Returns:
            IbanityAccount: The updated domain IbanityAccount model

        Raises:
            InvalidIbanityAccountError: If the IbanityAccount doesn't exist
                or data is invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def process_accounts_data(self, user, accounts_data: Dict[str, Any]) -> IbanityAccount:
        """Process raw accounts data from Ponto API and save or update
        in repository.

        Args:
            user: The user who owns the account
            accounts_data: Raw account data from Ponto API

        Returns:
            IbanityAccount: The created or updated account

        Raises:
            IbanityAccountDataError: If the account data is invalid
        """


class PontoTokenRepository(ABC):
    """Interface defining Ponto token data access operations.

    This abstract base class serves as a contract for PontoToken persistence
    operations. Any concrete implementation (e.g., Django ORM, SQLAlchemy,
    etc.) must implement all methods marked with @abstractmethod.

    The Repository pattern used here:
    1. Separates domain logic from data access details
    2. Makes the system more maintainable and testable
    3. Allows swapping different storage implementations without changing
       domain code
    4. Follows the Dependency Inversion Principle (SOLID)

    Example:
        class DjangoPontoTokenRepository(PontoTokenRepository):
            def save(self, ponto_token: PontoToken, user) -> PontoToken:
                # Implementation specific to PostgreSQL
                pass
    """

    @abstractmethod
    def save(self, ponto_token: PontoToken, user) -> PontoToken:
        """Save an Ponto token to the database.

        This method must either create a new Ponto token or update
        an existing one based on the user id. It should handle the persistence
        details while maintaining the domain model's integrity.

        Args:
            ponto_token (PontoToken): The domain PontoToken model to persist
            user (User): ID of the user who uploaded/created the
                Ibanity account

        Returns:
            PontoToken: The persisted domain PontoToken model, potentially with
                    updated metadata (e.g., ID, timestamps)

        Raises:
            InvalidPontoTokenError: If the PontoToken data is invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_by_id(self, ponto_token_id: int) -> Optional[PontoToken]:
        """Retrieve an PontoToken by id.

        Args:
            ponto_token_id (int): The PontoToken Model Id

        Returns:
            Optional[PontoToken]: The domain PontoToken model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_or_create_by_user(self, user, data: Dict[str, Any]) -> Tuple[PontoToken, bool]:
        """Get an existing token or create a new one.

        Args:
            user: The user who owns the token
            data: The token data

        Returns:
            Tuple[PontoToken, bool]: The token and whether it was created
        """

    @abstractmethod
    def get_by_user(self, user) -> PontoToken:
        """Get a token by user.

        Args:
            user: The user who owns the token

        Returns:
            PontoToken: The token data

        Raises:
            PontoTokenNotFoundError: If no token exists for the user
        """

    @abstractmethod
    def update_by_user(self, user, data: Dict[str, Any]) -> PontoToken:
        """Update a token by user.

        Args:
            user: The user who owns the token
            data: The updated token data

        Returns:
            PontoToken: The updated token
        """

    @abstractmethod
    def get_decrypted_access_token(self, user) -> str:
        """Get decrypted access token for a user.

        Args:
            user: The user to get the decrypted access token for

        Returns:
            str: The decrypted access token

        Raises:
            PontoTokenNotFoundError: If no token exists for the user
            PontoTokenDecryptionError: If there's an error decrypting the token
        """
