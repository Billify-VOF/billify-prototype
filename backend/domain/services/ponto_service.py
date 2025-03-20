"""Domain service for invoice business logic.

This service contains pure domain logic related to invoices,
independent of infrastructure concerns like storage or data transformation.
"""

import logging

from typing import Dict, Any
from domain.models.ponto import IbanityAccount, PontoToken
from domain.repositories.interfaces.ponto_repository import IbanityAccountRepository, PontoTokenRepository

from integrations.providers.ponto import PontoProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class IbanityAccountService:
    """Domain service that implements business logic for Ibanity account operations."""

    def __init__(self, ibanityAccountRepository: IbanityAccountRepository):
        self.ibanityAccountRepository = ibanityAccountRepository

    def update(
        self,
        ibanityAccount: IbanityAccount,
        extracted_data: Dict[str, Any]
    ) -> IbanityAccount:
        """Update an Ibanity account with data extracted from a document.

        This method applies business rules for updating an existing Ibanity account
        with extracted data, ensuring the domain model remains valid.

        Args:
            user (User): New database user instance
            account_id (str): New Ibanity Ponto Connect account id
            description (str): New Ibanity Ponto Connect account description
            product (str): 
            reference (str): 
            currency (str): New current Ponto account currency
            authorization_expiration_expected_at (datetime): New Ponto Connect authorization expiration time
            current_balance (Decimal): New current balance of the user Ponto account
            available_balance (Decimal): New available balance of the user Ponto account
            subtype (str): 
            holder_name (str): New Ponto account holder name
            resource_id (str): 

        Returns:
            The updated Ibanity account

        Raises:
            ValueError: If the extracted data is invalid
        """
        # Delegate to the domain model's update method
        ibanityAccount.update(
            user=extracted_data['user'],
            account_id = extracted_data['account_id'],
            description = extracted_data['description'],
            product = extracted_data['product'],
            reference = extracted_data['reference'],
            currency = extracted_data['currency'],
            authorization_expiration_expected_at = extracted_data['authorization_expiration_expected_at'],
            current_balance = extracted_data['current_balance'],
            available_balance = extracted_data['available_balance'],
            subtype = extracted_data['subtype'],
            holder_name = extracted_data['holder_name'],
            resource_id = extracted_data['resource_id'],
        )

        return ibanityAccount

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
            authorization_expiration_expected_at (datetime): Ponto Connect authorization expiration time
            current_balance (Decimal): Current balance of the user Ponto account
            available_balance (Decimal): Available balance of the user Ponto account
            subtype (str): 
            holder_name (str): Ponto account holder name
            resource_id (str): 

        Returns:
            A new IbanityAccount instance

        Raises:
            ValueError: If the extracted data is missing required fields
        """

        # Use the factory method to create and validate the Ibanity account
        return IbanityAccount.create(
            user=extracted_data['user'],
            account_id = extracted_data['account_id'],
            description = extracted_data['description'],
            product = extracted_data['product'],
            reference = extracted_data['reference'],
            currency = extracted_data['currency'],
            authorization_expiration_expected_at = extracted_data['authorization_expiration_expected_at'],
            current_balance = extracted_data['current_balance'],
            available_balance = extracted_data['available_balance'],
            subtype = extracted_data['subtype'],
            holder_name = extracted_data['holder_name'],
            resource_id = extracted_data['resource_id'],
        )
        
    
    def add_or_update(self, user, accounts_data):
        """Save or update account information in the database."""
        try:
            # Check if there are any accounts in the data
            if not accounts_data.get('data') or len(accounts_data['data']) == 0:
                return {"error": "No account data available"}
                
            # Validate account data structure
            account_info = accounts_data['data'][0]
            if 'id' not in account_info:
                return {"error": "Missing account ID in data"}
                
            if 'attributes' not in account_info:
                return {"error": "Missing attributes in account data"}
                
            attributes = account_info['attributes']
            required_attrs = ['description', 'product', 'reference', 'currency', 
                            'authorizationExpirationExpectedAt', 'currentBalance',
                            'availableBalance', 'subtype', 'holderName']
                            
            missing_attrs = [attr for attr in required_attrs if attr not in attributes]
            if missing_attrs:
                return {"error": f"Missing required attributes: {', '.join(missing_attrs)}"}
                
            # Validate meta data
            if ('meta' not in account_info or 
                'latestSynchronization' not in account_info['meta'] or
                'attributes' not in account_info['meta']['latestSynchronization'] or
                'resourceId' not in account_info['meta']['latestSynchronization']['attributes']):
                return {"error": "Missing resourceId in account data"}

            accountData = {
                'description': attributes['description'],
                'product': attributes['product'],
                'reference': attributes['reference'],
                'currency': attributes['currency'],
                'authorization_expiration_expected_at': attributes['authorizationExpirationExpectedAt'],
                'current_balance': attributes['currentBalance'],
                'available_balance': attributes['availableBalance'],
                'subtype': attributes['subtype'],
                'holder_name': attributes['holderName'],
                'resource_id': account_info['meta']['latestSynchronization']['attributes']['resourceId']
            }
            # Check if account already exists for the user
            account, created = self.ibanityAccountRepository.get_or_create(
                user=user,
                account_id=account_info['id'],
                data=accountData
            )
            
            if not created:
                account = self.ibanityAccountRepository.update_by_account_id(account_id=account_info['id'], data=accountData)
                return account
            
            return account
        
        except IndexError as e:
            logger.error(f"Invalid account data structure for user: {user.id}, error: {e}")
            return {"error": f"Invalid account data structure: {e}"}
        except KeyError as e:
            logger.error(f"Missing key in account data for user: {user.id}, error: {e}")
            return {"error": f"Missing data in account information: {e}"}
        except Exception as e:
            logger.error(f"Failed to save or update account for user: {user.id}, error: {e}")
            return {"error": f"Failed to save or update account: {e}"}

    # Get IbanityAccount data by user
    def get(self, user) -> IbanityAccount:
        """Get the IbanityAccount for a user.
        
        Args:
            user: The user who owns IbanityAccount for.
            
        Returns:
            IbanityAccount: The IbanityAccount data
            
        Raises:
            IbanityAccount.DoesNotExist: If no IbanityAccount exists for the user.
            Exception: If there's an error decrypting the token.
        """
        try:
            ibanityAccount = self.ibanityAccountRepository.get_by_user(user=user)
            return ibanityAccount
        except PontoToken.DoesNotExist as e:
            logger.error(f"Access token not found for user {user}")
            raise PontoToken.DoesNotExist(f"No token found for user {user}") from e
        except Exception as e:
            logger.error(f"Error retrieving access token for user {user}: {str(e)}")
            raise Exception(f"Error while retrieving the access token: {str(e)}") from e


class PontoTokenService:
    """Domain service that implements business logic for Ponto token operations."""

    def __init__(self, pontoTokenRepository: PontoTokenRepository):
        self.pontoTokenRepository = pontoTokenRepository

    def update(
        self,
        pontoToken: PontoToken,
        extracted_data: Dict[str, Any]
    ) -> PontoToken:
        """Update an Ponto token with data extracted from a document.

        This method applies business rules for updating an existing Ponto token
        with extracted data, ensuring the domain model remains valid.

        Args:
            user (User): Represents User that owns this Ponto token
            access_token (str): Access token for API access to Ponto
            refresh_token (str): Refresh token for API access to Ponto
            expires_in (int): Access token expiration time in milliseconds
            created_at (datetime): Created at timestamp for this record
            updated_at (datetime): Updated at timestamp for this record

        Returns:
            The updated Ponto token

        Raises:
            ValueError: If the extracted data is invalid
        """
        # Delegate to the domain model's update method
        pontoToken.update(
            user=extracted_data['user'],
            access_token = extracted_data['access_token'],
            refresh_token = extracted_data['refresh_token'],
            expires_in = extracted_data['expires_in'],
        )

        return pontoToken

    def create(
        self,
        extracted_data: Dict[str, Any]
    ) -> PontoToken:
        """Create a new Ponto token from extracted document data.

        This method applies business rules for creating a new Ponto token
        from extracted data, ensuring all required fields are present
        and valid.

        Args:
            user (User): Represents User that owns this Ponto token
            access_token (str): Access token for API access to Ponto
            refresh_token (str): Refresh token for API access to Ponto
            expires_in (int): Access token expiration time in milliseconds
            created_at (datetime): Created at timestamp for this record
            updated_at (datetime): Updated at timestamp for this record

        Returns:
            A new PontoToken instance

        Raises:
            ValueError: If the extracted data is missing required fields
        """

        # Use the factory method to create and validate the Ponto token
        return PontoToken.create(
            user=extracted_data['user'],
            access_token = extracted_data['access_token'],
            refresh_token = extracted_data['refresh_token'],
            expires_in = extracted_data['expires_in'],
        )

    # Get access token from Ponto token model
    def get_access_token(self, user) -> str:
        """Get the access token for a user.
        
        Args:
            user: The user to get the access token for.
            
        Returns:
            str: The decrypted access token.
            
        Raises:
            PontoToken.DoesNotExist: If no token exists for the user.
            Exception: If there's an error decrypting the token.
        """
        try:
            pontoToken = self.pontoTokenRepository.get_by_user(user=user)
            access_token = PontoProvider.decrypt_token(pontoToken.access_token)
            return access_token
        except PontoToken.DoesNotExist as e:
            logger.error(f"Access token not found for user {user}")
            raise PontoToken.DoesNotExist(f"No token found for user {user}") from e
        except Exception as e:
            logger.error(f"Error retrieving access token for user {user}: {str(e)}")
            raise Exception(f"Error while retrieving the access token: {str(e)}") from e
        
    # Get or create PontoToken model from payload
    def add_or_update(self, user, data):
        """Get or create PontoToken model from payload

        Args:
            data (dict): A dictionary containing the following keys:
                - access_token (str): The access token.
                - refresh_token (str): The refresh token.
                - expires_in (int): The expiration time in seconds.
                
        Returns:
            PontoToken: An instance of the PontoToken model.
            created: Represent if the PontoToken created or not
        """
        try:
            pontoToken, created = self.pontoTokenRepository.get_or_create_by_user(user, data)

            if not created:  # If the Ponto token already exists, update it
                updatedPontoToken = self.pontoTokenRepository.update_by_user(user=user, data=data)
                return updatedPontoToken

            return pontoToken
        except Exception as e:
            logger.error(f"Error while getting or creating access token for user {user}: {str(e)}")
            raise Exception(f"Error while getting or creating the access token: {str(e)}") from e

    # Get PontoToken data from Ponto token model by user
    def get(self, user) -> PontoToken:
        """Get the PontoToken for a user.
        
        Args:
            user: The user to get the access token for.
            
        Returns:
            PontoToken: The PontoToken data
            
        Raises:
            PontoToken.DoesNotExist: If no token exists for the user.
            Exception: If there's an error decrypting the token.
        """
        try:
            pontoToken = self.pontoTokenRepository.get_by_user(user=user)
            return pontoToken
        except PontoToken.DoesNotExist as e:
            logger.error(f"Access token not found for user {user}")
            raise PontoToken.DoesNotExist(f"No token found for user {user}") from e
        except Exception as e:
            logger.error(f"Error retrieving access token for user {user}: {str(e)}")
            raise Exception(f"Error while retrieving the access token: {str(e)}") from e
