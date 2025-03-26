"""Domain service for Ponto business logic.

This service contains pure domain logic related to Ponto,
independent of infrastructure concerns like storage or data transformation.
"""

import logging

from typing import Dict, Any
from domain.models.ponto import IbanityAccount, PontoToken
from domain.exceptions import (
    PontoTokenNotFoundError, PontoTokenDecryptionError,
    PontoTokenCreationError, IbanityAccountNotFoundError,
    IbanityAccountDataError
)
from domain.repositories.interfaces.ponto_repository import (
    IbanityAccountRepository, PontoTokenRepository
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class IbanityAccountService:
    """
    Domain service that implements business logic for Ibanity account
    operations.
    """

    def __init__(self, ibanity_account_repository: IbanityAccountRepository):
        """Initialize the service with required dependencies.
        
        Note: Prefer using the factory method 'create' instead of direct initialization.
        
        Args:
            ibanity_account_repository (IbanityAccountRepository): Repository for 
                accessing and persisting Ibanity account data.
        """
        self.ibanity_account_repository = ibanity_account_repository

    def update(
        self,
        ibanity_account: IbanityAccount,
        extracted_data: Dict[str, Any]
    ) -> IbanityAccount:
        """Update an Ibanity account with data extracted from a document.

        This method applies business rules for updating an existing Ibanity
        account with extracted data, ensuring the domain model remains valid.

        Args:
            user (User): New database user instance
            account_id (str): New Ibanity Ponto Connect account id
            description (str): New Ibanity Ponto Connect account description
            product (str):
            reference (str):
            currency (str): New current Ponto account currency
            authorization_expiration_expected_at (datetime): New Ponto Connect
                authorization expiration time
            current_balance (Decimal): New current balance of the user Ponto
                account
            available_balance (Decimal): New available balance of the user
                Ponto account
            subtype (str):
            holder_name (str): New Ponto account holder name
            resource_id (str):

        Returns:
            The updated Ibanity account

        Raises:
            IbanityAccountDataError: If the extracted data is invalid or
                missing required fields
        """
        required_fields = [
            'user',
            'account_id',
            'description',
            'product',
            'reference',
            'currency',
            'authorization_expiration_expected_at',
            'current_balance',
            'available_balance',
            'subtype',
            'holder_name',
            'resource_id'
        ]

        # Validate that all required fields exist
        missing_fields = [
            field for field in required_fields
            if field not in extracted_data
        ]
        if missing_fields:
            raise IbanityAccountDataError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            # Delegate to the domain model's update method
            ibanity_account.update(
                user=extracted_data['user'],
                account_id=extracted_data['account_id'],
                description=extracted_data['description'],
                product=extracted_data['product'],
                reference=extracted_data['reference'],
                currency=extracted_data['currency'],
                authorization_expiration_expected_at=(
                    extracted_data['authorization_expiration_expected_at']
                ),
                current_balance=extracted_data['current_balance'],
                available_balance=extracted_data['available_balance'],
                subtype=extracted_data['subtype'],
                holder_name=extracted_data['holder_name'],
                resource_id=extracted_data['resource_id'],
            )

            return ibanity_account
        except KeyError as e:
            raise IbanityAccountDataError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise IbanityAccountDataError(f"Error updating account: {str(e)}")

    def create(
        self,
        extracted_data: Dict[str, Any]
    ) -> IbanityAccount:
        """Create a new Ibanity account from extracted document data.

        This method applies business rules for creating a new Ibanity account
        from extracted data, ensuring all required fields are present
        and valid.

        Args:
            user (User): Database user instance
            account_id (str): Ibanity Ponto Connect account id
            description (str): Ibanity Ponto Connect account description
            product (str):
            reference (str):
            currency (str): Current Ponto account currency
            authorization_expiration_expected_at (datetime): Ponto Connect
                authorization expiration time
            current_balance (Decimal): Current balance of the user Ponto
                account
            available_balance (Decimal): Available balance of the user
                Ponto account
            subtype (str):
            holder_name (str): Ponto account holder name
            resource_id (str):

        Returns:
            A new IbanityAccount instance

        Raises:
            IbanityAccountDataError: If the extracted data is missing
                required fields
        """
        required_fields = [
            'user', 'account_id', 'description', 'product', 'reference',
            'currency', 'authorization_expiration_expected_at',
            'current_balance', 'available_balance', 'subtype',
            'holder_name', 'resource_id'
        ]

        # Validate that all required fields exist
        missing_fields = [field for field in required_fields
                          if field not in extracted_data]
        if missing_fields:
            raise IbanityAccountDataError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            # Use the factory method to create and validate the Ibanity account
            return IbanityAccount.create(
                user=extracted_data['user'],
                account_id=extracted_data['account_id'],
                description=extracted_data['description'],
                product=extracted_data['product'],
                reference=extracted_data['reference'],
                currency=extracted_data['currency'],
                authorization_expiration_expected_at=(
                    extracted_data['authorization_expiration_expected_at']
                ),
                current_balance=extracted_data['current_balance'],
                available_balance=extracted_data['available_balance'],
                subtype=extracted_data['subtype'],
                holder_name=extracted_data['holder_name'],
                resource_id=extracted_data['resource_id'],
            )
        except KeyError as e:
            raise IbanityAccountDataError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise IbanityAccountDataError(f"Error creating account: {str(e)}")

    def add_or_update(
        self,
        user: Any,  # User model instance
        accounts_data: Dict[str, Any]
    ) -> IbanityAccount:
        """Save or update account information from Ponto API in the database.

        Args:
            user: The user who owns the account
            accounts_data: Raw account data from Ponto API response
                Expected to contain 'data' list with account information

        Returns:
            IbanityAccount: The created or updated account when successful

        Raises:
            IbanityAccountDataError: If the account data is invalid
            IbanityAccountNotFoundError: If the account cannot be found or
            created
        """
        try:
            # Process account data through the repository
            return self.ibanity_account_repository.process_accounts_data(
                user=user,
                accounts_data=accounts_data
            )
        except IndexError as e:
            logger.error(
                f"Invalid account structure for user: {user.id}, error: {e}"
            )
            raise IbanityAccountDataError(
                f"Invalid account data structure: {e}"
            )
        except KeyError as e:
            logger.error(
                f"Missing key in account data for user: {user.id}, error: {e}"
            )
            raise IbanityAccountDataError(
                f"Missing data in account information: {e}"
            )
        except Exception as e:
            logger.error(
                f"Failed to save or update account for user: {user.id}, "
                f"error: {e}"
            )
            raise IbanityAccountDataError(
                f"Failed to save or update account: {e}"
            )

    # Get IbanityAccount data by user
    def get(self, user: Any) -> IbanityAccount:
        """Get the IbanityAccount for a user.

        Args:
            user: The user who owns the IbanityAccount.

        Returns:
            IbanityAccount: The IbanityAccount data

        Raises:
            IbanityAccountNotFoundError: If no IbanityAccount exists for
                the user
            IbanityAccountDataError: If there's an error retrieving
                account data
        """
        try:
            return self.ibanity_account_repository.get_by_user(user=user)
        except IbanityAccountNotFoundError:
            # Log and re-raise domain exception directly
            logger.error(f"Account not found for user {user}")
            raise
        except Exception as e:
            # For unexpected errors, preserve context with detailed logging
            logger.error(
                f"Error retrieving IbanityAccount for user {user}",
                exc_info=True
            )
            raise IbanityAccountDataError(
                "Error retrieving account data"
            ) from e


class PontoTokenService:
    """
    Domain service that implements business logic for Ponto token
    operations.
    """

    @classmethod
    def create(
        cls, ponto_token_repository: PontoTokenRepository
    ) -> 'PontoTokenService':
        """Create a properly configured PontoTokenService instance.

        Args:
            ponto_token_repository: Repository for Ponto token operations.

        Returns:
            A validated PontoTokenService instance

        Raises:
            ValueError: If dependencies are missing or invalid
        """
        if ponto_token_repository is None:
            raise ValueError("ponto_token_repository cannot be None")

        return cls(ponto_token_repository)

    def __init__(self, ponto_token_repository: PontoTokenRepository):
        """Initialize the service with required dependencies.

        Args:
            ponto_token_repository: Repository for Ponto token operations.
        """
        self.ponto_token_repository = ponto_token_repository

    def update(
        self,
        ponto_token: PontoToken,
        extracted_data: Dict[str, Any]
    ) -> PontoToken:
        """Update a Ponto token with data extracted from a document.

        This method applies business rules for updating an existing Ponto token
        with extracted data, ensuring the domain model remains valid.

        Args:
            pontoToken: The token object to update
            extracted_data: Dictionary containing token data with these keys:
                - user: User that owns this token
                - access_token: Access token for Ponto API
                - refresh_token: Refresh token for Ponto API
                - expires_in: Access token expiration time in milliseconds

        Returns:
            The updated Ponto token

        Raises:
            PontoTokenCreationError: If the extracted data is invalid or
                missing required fields
        """
        required_fields = [
            'user', 'access_token', 'refresh_token', 'expires_in'
        ]

        # Validate that all required fields exist
        missing_fields = [
            field for field in required_fields
            if field not in extracted_data
        ]
        if missing_fields:
            raise PontoTokenCreationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            # Delegate to the domain model's update method
            ponto_token.update(
                user=extracted_data['user'],
                access_token=extracted_data['access_token'],
                refresh_token=extracted_data['refresh_token'],
                expires_in=extracted_data['expires_in'],
            )

            return ponto_token
        except KeyError as e:
            raise PontoTokenCreationError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise PontoTokenCreationError(f"Error updating token: {str(e)}")

    def create_token(
        self,
        extracted_data: Dict[str, Any]
    ) -> PontoToken:
        """Create a new Ponto token from extracted document data.

        This method applies business rules for creating a new Ponto token
        from extracted data, ensuring all required fields are present
        and valid.

        Args:
            extracted_data: Dictionary containing token data with these keys:
                - user: User that owns this token
                - access_token: Access token for Ponto API
                - refresh_token: Refresh token for Ponto API
                - expires_in: Access token expiration time in milliseconds

        Returns:
            A new PontoToken instance

        Raises:
            PontoTokenCreationError: If the extracted data is missing
                required fields
        """
        required_fields = [
            'user', 'access_token', 'refresh_token', 'expires_in'
        ]

        # Validate that all required fields exist
        missing_fields = [
            field for field in required_fields
            if field not in extracted_data
        ]
        if missing_fields:
            raise PontoTokenCreationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            # Use the factory method to create and validate the Ponto token
            return PontoToken.create(
                user=extracted_data['user'],
                access_token=extracted_data['access_token'],
                refresh_token=extracted_data['refresh_token'],
                expires_in=extracted_data['expires_in'],
            )
        except KeyError as e:
            raise PontoTokenCreationError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise PontoTokenCreationError(f"Error creating token: {str(e)}")

    # Get access token from Ponto token model
    def decrypt_access_token_for_user(self, user: Any) -> str:
        """Get the decrypted access token for a user.

        Args:
            user: The user to get the access token for.

        Returns:
            str: The decrypted access token.

        Raises:
            PontoTokenNotFoundError: If no token exists for the user.
            PontoTokenDecryptionError: If there's an error decrypting
                the token.
        """
        try:
            # Use repository for decryption (proper layer separation)
            return self.ponto_token_repository.get_decrypted_access_token(
                user=user
            )
        except PontoToken.DoesNotExist:  # type: ignore
            logger.error(f"Access token not found for user {user}")
            raise PontoTokenNotFoundError(f"No token found for user {user}")
        except PontoTokenDecryptionError as e:
            # Re-raise decryption errors directly
            logger.error(f"Error decrypting token for user {user}: {str(e)}")
            raise
        except IbanityAccountDataError as e:
            # Handle possible repository errors
            logger.error(f"Invalid token data for user {user}: {str(e)}")
            raise PontoTokenDecryptionError(
                f"Invalid token data: {str(e)}"
            ) from e
        except Exception as e:
            # Fallback for unexpected errors
            logger.error(
                f"Unexpected error retrieving token for user {user}: {str(e)}",
                exc_info=True
            )
            raise PontoTokenDecryptionError(
                f"Error while retrieving the access token: {str(e)}"
            ) from e

    def add_or_update(self, user: Any, data):
        """Apply domain rules to create or update a Ponto token.

        Args:
            user: The user who owns the token
            data: Dictionary containing token data with these keys:
                - access_token: Access token for Ponto API
                - refresh_token: Refresh token for Ponto API
                - expires_in: Access token expiration time in milliseconds

        Returns:
            PontoToken: The created or updated token

        Raises:
            PontoTokenCreationError: If data is invalid or creation fails
            PontoTokenDecryptionError: If existing token cannot be read
        """
        # 1. Validate input data structure
        required_fields = ['access_token', 'refresh_token', 'expires_in']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            raise PontoTokenCreationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            # 2. Check if token exists with domain-specific rules
            try:
                existing_token = self.ponto_token_repository.get_by_user(
                    user=user
                )

                # 3. Apply domain logic - check if update is needed
                if (existing_token.access_token != data['access_token']
                        or existing_token.refresh_token
                        != data['refresh_token']
                        or existing_token.expires_in != data['expires_in']):

                    # 4. Update existing token through domain model
                    existing_token.update(
                        user=user,
                        access_token=data['access_token'],
                        refresh_token=data['refresh_token'],
                        expires_in=data['expires_in']
                    )
                    return self.ponto_token_repository.save(existing_token, user)

                return existing_token

            except PontoToken.DoesNotExist:  # type: ignore
                # 5. Token doesn't exist, create new one using domain factory
                new_token = PontoToken.create(
                    user=user,
                    access_token=data['access_token'],
                    refresh_token=data['refresh_token'],
                    expires_in=data['expires_in']
                )
                return self.ponto_token_repository.save(new_token, user)

        except PontoTokenNotFoundError:
            # Handle specific domain exception
            raise PontoTokenCreationError(
                "Token not found and creation failed"
            )
        except PontoTokenDecryptionError:
            # Re-raise specific domain exceptions
            raise
        except Exception as e:
            logger.error(f"Error processing token for user {user}: {str(e)}")
            raise PontoTokenCreationError(
                f"Error processing token: {str(e)}"
            ) from e

    # Get PontoToken data from Ponto token model by user
    def get_token_for_user(self, user: Any) -> PontoToken:
        """Get the PontoToken model for a user.

        Args:
            user: The user to get the token for.

        Returns:
            PontoToken: The PontoToken data

        Raises:
            PontoTokenNotFoundError: If no token exists for the user.
            PontoTokenDecryptionError: If there's an error retrieving
                the token.
        """
        try:
            ponto_token = self.ponto_token_repository.get_by_user(user=user)
            return ponto_token
        except PontoToken.DoesNotExist:  # type: ignore
            logger.error(f"Access token not found for user {user}")
            raise PontoTokenNotFoundError(f"No token found for user {user}")
        except Exception as e:
            logger.error(
                f"Error retrieving access token for user {user}: {str(e)}"
            )
            raise PontoTokenDecryptionError(
                f"Error while retrieving the access token: {str(e)}"
            ) from e
