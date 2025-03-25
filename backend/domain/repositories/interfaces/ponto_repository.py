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
        def save(self, ibanityAccount: IbanityAccount, user) -> IbanityAccount:
            # Implementation specific to PostgreSQL
            pass
"""

from abc import ABC, abstractmethod
from typing import Optional

from django.contrib.auth.models import User
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
            def save(self, ibanityAccount: IbanityAccount, user) -> IbanityAccount:
                # Implementation specific to PostgreSQL
                pass
    """

    @abstractmethod
    def save(self, ibanityAccount: IbanityAccount, user: User) -> IbanityAccount:
        """Save an ibanity account to the database.

        This method must either create a new Ibanity account or update an existing one
        based on the user id. It should handle the persistence details
        while maintaining the domain model's integrity.

        Args:
            ibanityAccount (IbanityAccount): The domain Ibanity account model to persist
            user (User): User instance who uploaded/created the Ibanity account

        Returns:
            IbanityAccount: The persisted domain IbanityAccount model, potentially with
                    updated metadata (e.g., ID, timestamps)

        Raises:
            InvalidIbanityAccountError: If the IbanityAccount data is invalid
            RepositoryError: If there's a persistence-related error
        """
        
    @abstractmethod
    def get_or_create(self, user: User, account_id: str, data: dict) -> IbanityAccount, bool:
        """Get or create by user or account_id and saves with the provided data

        Args:
            user (User): Ibanity account owner
            account_id (str): Ibanity account ID
            data (dict): New data or replace data
                - 'description': Description of IbanityAccount
                - 'product': Product
                - 'reference': Reference
                - 'currency': Currency
                - 'authorization_expiration_expected_at': Authorization expiration time
                - 'current_balance': Current balance
                - 'available_balance': Available balance
                - 'subtype': Subtype
                - 'holder_name': Holder name
                - 'resource_id': Resource ID

        Returns:
            IbanityAccount: Return IbanityAccount Model data
            bool: Return true if the model created, otherwise false
        """
        
    @abstractmethod
    def get_by_id(self, ibanityAccount_id: int) -> Optional[IbanityAccount]:
        """Retrieve an IbanityAccount by id.

        Args:
            ibanityAccount_id (int): IbanityAccount Model Id

        Returns:
            Optional[IbanityAccount]: The domain IbanityAccount model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def get_by_user(self, user) -> Optional[IbanityAccount]:
        """Retrieve an IbanityAccount by user id.

        Args:
            user (User): The user instance

        Returns:
            Optional[IbanityAccount]: The domain IbanityAccount model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
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
    def update(self, ibanityAccount: IbanityAccount, user) -> IbanityAccount:
        """Update an existing IbanityAccount.

        This method should update all fields of an existing IbanityAccount while
        maintaining any metadata (e.g., created_at timestamp).

        Args:
            ibanityAccount (IbanityAccount): The domain IbanityAccount with updated data
            user (User): User instance performing the update

        Returns:
            IbanityAccount: The updated domain IbanityAccount model

        Raises:
            InvalidIbanityAccountError: If the IbanityAccount doesn't exist or data is
                               invalid
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def update_by_account_id(self, account_id: str, data: dict) -> IbanityAccount:
        """Update an existing IbanityAccount.

        This method should update all fields of an existing IbanityAccount while
        maintaining any metadata (e.g., created_at timestamp).

        Args:
            account_id (str): The IbanityAccount account_id
            data (dict): New data or replace data
                - 'description': Description of IbanityAccount
                - 'product': Product
                - 'reference': Reference
                - 'currency': Currency
                - 'authorization_expiration_expected_at': Authorization expiration time
                - 'current_balance': Current balance
                - 'available_balance': Available balance
                - 'subtype': Subtype
                - 'holder_name': Holder name
                - 'resource_id': Resource ID

        Returns:
            IbanityAccount: The updated domain IbanityAccount model

        Raises:
            InvalidIbanityAccountError: If the IbanityAccount doesn't exist or data is
                               invalid
            RepositoryError: If there's a persistence-related error
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
            def save(self, pontoToken: PontoToken, user) -> PontoToken:
                # Implementation specific to PostgreSQL
                pass
    """

    @abstractmethod
    def save(self, pontoToken: PontoToken, user) -> PontoToken:
        """Save an Ponto token to the database.

        This method must either create a new Ponto token or update an existing one
        based on the user id. It should handle the persistence details
        while maintaining the domain model's integrity.

        Args:
            pontoToken (PontoToken): The domain PontoToken model to persist
            user (User): ID of the user who uploaded/created the Ibanity account

        Returns:
            PontoToken: The persisted domain PontoToken model, potentially with
                    updated metadata (e.g., ID, timestamps)

        Raises:
            InvalidPontoTokenError: If the PontoToken data is invalid
            RepositoryError: If there's a persistence-related error
        """
    
    @abstractmethod    
    def get_by_id(self, pontoToken_id: int) -> Optional[PontoToken]:
        """Retrieve an PontoToken by id.

        Args:
            pontoToken_id (int): The PontoToken Model Id

        Returns:
            Optional[PontoToken]: The domain PontoToken model if found,
                             None otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """
        

    @abstractmethod
    def get_or_create_by_user(self, user: User, data: dict) -> PontoToken, bool:
        """Retrieve an PontoToken by user id.

        Args:
            user (User): The user instance
            data (dict): A dictionary containing the following keys:
                - access_token (str): The access token.
                - refresh_token (str): The refresh token.
                - expires_in (int): The expiration time in seconds.

        Returns:
            PontoToken: The domain PontoToken model if found,
                             otherwise the created one
            bool: Returns true if the model is created,
                        false otherwise

        Raises:
            RepositoryError: If there's a persistence-related error
        """

    @abstractmethod
    def update_by_user(self, user: User, data: dict) -> PontoToken:
        """Update an existing PontoToken.

        This method should update all fields of an existing PontoToken while
        maintaining any metadata (e.g., created_at timestamp).

        Args:
            user (User): ID of the user performing the update
            data (dict): A dictionary containing the following keys:
                - access_token (str): The access token.
                - refresh_token (str): The refresh token.
                - expires_in (int): The expiration time in seconds.

        Returns:
            PontoToken: The updated domain PontoToken model

        Raises:
            InvalidPontoTokenError: If the PontoToken doesn't exist or data is
                               invalid
            RepositoryError: If there's a persistence-related error
        """