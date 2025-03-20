"""Domain model representing an invoice and its business rules."""

from decimal import Decimal
from logging import getLogger
from datetime import datetime

from domain.exceptions import InvalidIbanityAccountError

# Module-level logger
logger = getLogger(__name__)


class IbanityAccount:
    """
    Represents an Ibanity account in our system, containing all relevant
    business data and validation rules.

    Attributes:
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
    """

    @classmethod
    def create(cls,
               user,
               account_id: str,
               description: str,
               product: str,
               reference: str,
               currency: str,
               authorization_expiration_expected_at: datetime,
               current_balance: Decimal,
               available_balance: Decimal,
               subtype: str,
               holder_name: str,
               resource_id: str
               ) -> 'IbanityAccount':
        """Create a new valid IbanityAccount.

        Factory method that creates and validates a new Ibanity account instance.
        Use this method instead of constructor for normal Ibanity account creation.

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
            IbanityAccount: A validated Ibanity account instance

        Raises:
            InvalidIbanityAccountError: If any of the data is invalid
        """
        ibanityAccount = cls(
            user=user,
            account_id=account_id,
            description=description,
            product=product,
            reference=reference,
            currency=currency,
            authorization_expiration_expected_at=authorization_expiration_expected_at,
            current_balance=current_balance,
            available_balance=available_balance,
            subtype=subtype,
            holder_name=holder_name,
            resource_id=resource_id,
        )
        ibanityAccount.validate()
        return ibanityAccount

    def __init__(
        self,
        *,  # This makes all following arguments keyword-only
        user,
        account_id: str,
        description: str,
        product: str,
        reference: str,
        currency: str,
        authorization_expiration_expected_at: datetime,
        current_balance: Decimal,
        available_balance: Decimal,
        subtype: str,
        holder_name: str,
        resource_id: str
    ) -> None:
        logger.debug("IbanityAccount __init__ called")
        logger.debug(f"  User: {user} ({type(user)})")
        logger.debug(f"  Account ID: {account_id} ({type(account_id)})")
        logger.debug(f"  Current balance: {current_balance} ({type(current_balance)})")
        self.user = user
        self.account_id: str = account_id
        self.description: str = description
        self.product: str = product
        self.reference: str = reference
        self.currency: str = currency
        self.authorization_expiration_expected_at: datetime = authorization_expiration_expected_at
        self.current_balance: Decimal = current_balance
        self.available_balance: Decimal = available_balance
        self.subtype: str = subtype
        self.holder_name: str = holder_name
        self.resource_id: str = resource_id

    def validate(self) -> None:
        """Apply business rules to validate IbanityAccount data."""
        if self.current_balance < 0:
            raise InvalidIbanityAccountError("IbanityAccount current balance can't be negative")
        
        if self.available_balance < 0:
            raise InvalidIbanityAccountError("IbanityAccount available balance can't be negative")

    def update(
        self,
        *,
        user = None,
        account_id: str = None,
        description: str = None,
        product: str = None,
        reference: str = None,
        currency: str = None,
        authorization_expiration_expected_at: datetime = None,
        current_balance: Decimal = None,
        available_balance: Decimal = None,
        subtype: str = None,
        holder_name: str = None,
        resource_id: str = None
    ) -> None:
        """Update IbanityAccount fields with validation.

        This method allows updating one or more IbanityAccount fields and ensures
        that all business rules are validated after the update.

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

        Raises:
            InvalidIbanityAccountError: If the updated data violates business rules

        Example:
            ibanityAccount = IbanityAccount(user=user, account_id="8ba2c6b6-180c-4c13-93e3-879a1f8d305d",
                             ...)

            # Update just the description
            ibanityAccount.update(description="description")

            # Update multiple fields
            ibanityAccount.update(
                description="description",
                currency="USD",
            )
        """
        # Update fields that are provided (not None)
        if user is not None:
            self.user = user

        if account_id is not None:
            self.account_id = account_id
            
        if description is not None:
            self.description = description
            
        if product is not None:
            self.product = product
            
        if reference is not None:
            self.reference = reference
            
        if currency is not None:
            self.currency = currency
            
        if authorization_expiration_expected_at is not None:
            self.authorization_expiration_expected_at = authorization_expiration_expected_at
            
        if current_balance is not None:
            self.current_balance = current_balance
            
        if available_balance is not None:
            self.available_balance = available_balance
            
        if subtype is not None:
            self.subtype = subtype
            
        if holder_name is not None:
            self.holder_name = holder_name
            
        if resource_id is not None:
            self.resource_id = resource_id

        # Validate the updated invoice
        self.validate()


class PontoToken:
    """
    Represents an Ponto token in our system, containing all relevant
    business data and validation rules.

    Attributes:
        user (User): Represents User that owns this Ponto token
        access_token (str): Access token for API access to Ponto
        refresh_token (str): Refresh token for API access to Ponto
        expires_in (int): Access token expiration time in milliseconds
        created_at (datetime): Created at timestamp for this record
        updated_at (datetime): Updated at timestamp for this record
    """

    @classmethod
    def create(cls,
               user,
               access_token: str,
               refresh_token: str,
               expires_in: int,
               ) -> 'PontoToken':
        """Create a new valid PontoToken.

        Factory method that creates and validates a new PontoToken instance.
        Use this method instead of constructor for normal PontoToken creation.

        Args:
            user (User): Represents User that owns this Ponto token
            access_token (str): Access token for API access to Ponto
            refresh_token (str): Refresh token for API access to Ponto
            expires_in (int): Access token expiration time in milliseconds
            created_at (datetime): Created at timestamp for this record
            updated_at (datetime): Updated at timestamp for this record

        Returns:
            PontoToken: A validated PontoToken instance

        Raises:
            InvalidPontoTokenError: If any of the data is invalid
        """
        pontoToken = cls(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )
        pontoToken.validate()
        return pontoToken

    def __init__(
        self,
        *,  # This makes all following arguments keyword-only
        user,
        access_token: str,
        refresh_token: str,
        expires_in: int
    ) -> None:
        logger.debug("PontoToken __init__ called")
        logger.debug(f"  User: {user} ({type(user)})")
        logger.debug(f"  Access Token: {access_token} ({type(access_token)})")
        logger.debug(f"  Refresh Token: {refresh_token} ({type(refresh_token)})")
        logger.debug(f"  Expires in: {expires_in} ({type(expires_in)})")
        self.user = user
        self.access_token: str = access_token
        self.refresh_token: str = refresh_token
        self.expires_in: int = expires_in

    def validate(self) -> None:
        """Apply business rules to validate PontoToken data."""

    def update(
        self,
        *,
        user,
        access_token: str = None,
        refresh_token: str = None,
        expires_in: int = None,
    ) -> None:
        """Update PontoToken fields with validation.

        This method allows updating one or more PontoToken fields and ensures
        that all business rules are validated after the update.

        Args:
            user (User): Represents User that owns this Ponto token
            access_token (str): Access token for API access to Ponto
            refresh_token (str): Refresh token for API access to Ponto
            expires_in (int): Access token expiration time in milliseconds
            created_at (datetime): Created at timestamp for this record
            updated_at (datetime): Updated at timestamp for this record

        Raises:
            InvalidPontoTokenError: If the updated data violates business rules

        Example:
            pontoToken = PontoToken(user=user, access_token="access token",
                             ...)

            # Update just the access_token
            pontoToken.update(access_token="new access token")

            # Update multiple fields
            pontoToken.update(
                access_token="access token",
                refresh_token="refresh token",
            )
        """
        # Update fields that are provided (not None)
        if user is not None:
            self.user = user

        if access_token is not None:
            self.access_token = access_token
            
        if refresh_token is not None:
            self.refresh_token = refresh_token
            
        if expires_in is not None:
            self.expires_in = expires_in

        # Validate the updated invoice
        self.validate()
