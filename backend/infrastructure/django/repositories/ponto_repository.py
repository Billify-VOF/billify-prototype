"""Django ORM implementation of the Ponto-related repository interfaces."""

from typing import Optional, Dict, Any, Tuple
from django.core.exceptions import ObjectDoesNotExist
from domain.repositories.interfaces.ponto_repository import (
    IbanityAccountRepository,
    PontoTokenRepository
)
from domain.models.ponto import (
    IbanityAccount as DomainIbanityAccount,
    PontoToken as DomainPontoToken
)
from domain.exceptions import (
    InvalidIbanityAccountError,
    InvalidPontoTokenError,
    IbanityAccountDataError,
    PontoTokenNotFoundError,
    PontoTokenDecryptionError
)
from infrastructure.django.models.ponto import (
    IbanityAccount as DjangoIbanityAccount,
    PontoToken as DjangoPontoToken
)
from logging import getLogger

# Module-level logger
logger = getLogger(__name__)


class DjangoIbanityAccountRepository(IbanityAccountRepository):
    """Django ORM implementation of the IbanityAccount repository."""

    def _to_domain(
        self, db_ibanity_account: DjangoIbanityAccount
    ) -> DomainIbanityAccount:
        """Convert Django model to domain model.

        This method is used:
        1. When fetching data from the database
        2. Before returning data to business logic layer

        What it does:
        1. Takes database fields and maps them to domain model attributes
        2. Preserves the database ID for future reference
        3. Ensures data is in the format our domain logic expects

        Note:
            The `id` field is automatically provided by Django's ORM.
            Every Django model gets an auto-incrementing integer primary key
            field named 'id' unless explicitly specified otherwise.

        Args:
            db_ibanity_account: Django ORM IbanityAccount model instance

        Returns:
            DomainIbanityAccount: Domain model populated with database values

        Example:
            # When fetching by ID:
            db_ibanity_account = DjangoIbanityAccount.objects.get(id=123)
            domain_ibanity_account = self._to_domain(db_ibanity_account)
            return domain_ibanity_account  # Ready for business logic
        """
        logger.debug(
            "Converting DB IbanityAccount to domain model: %s",
            db_ibanity_account
        )
        # All Django models have an id field by default
        ibanity_account_args = {
            'user': db_ibanity_account.user,
            'account_id': db_ibanity_account.account_id,
            'description': db_ibanity_account.description,
            'product': db_ibanity_account.product,
            'reference': db_ibanity_account.reference,
            'currency': db_ibanity_account.currency,
            'authorization_expiration_expected_at': (
                db_ibanity_account.authorization_expiration_expected_at
            ),
            'current_balance': db_ibanity_account.current_balance,
            'available_balance': db_ibanity_account.available_balance,
            'subtype': db_ibanity_account.subtype,
            'holder_name': db_ibanity_account.holder_name,
            'resource_id': db_ibanity_account.resource_id,
            # Map Django's auto-generated id to domain model's
            # ibanity_account_id parameter. Domain model stores it as self.id
            'ibanity_account_id': db_ibanity_account.id  # type: ignore
        }

        return DomainIbanityAccount(**ibanity_account_args)

    def _to_django(
        self,
        domain_ibanity_account: DomainIbanityAccount,
    ) -> DjangoIbanityAccount:
        """Convert domain model to Django model.

        This method is used:
        1. When saving new IbanityAccounts to database
        2. When updating existing IbanityAccounts

        What it does:
        1. Takes domain model attributes and maps them to database fields
        2. Adds necessary database-specific information (like user)
        3. Prepares data for database storage

        Args:
            domain_ibanity_account: Domain model instance to convert
            user: User instance who owns this IbanityAccount

        Returns:
            DjangoIbanityAccount: Django ORM model ready for
            database operations

        Example:
            # When saving a new IbanityAccount:
            db_ibanity_account = self._to_django(domain_ibanity_account, user)
            db_ibanity_account.save()
            return self._to_domain(db_ibanity_account)
        """

        return DjangoIbanityAccount(
            user=domain_ibanity_account.user,
            account_id=domain_ibanity_account.account_id,
            description=domain_ibanity_account.description,
            product=domain_ibanity_account.product,
            reference=domain_ibanity_account.reference,
            currency=domain_ibanity_account.currency,
            authorization_expiration_expected_at=(
                domain_ibanity_account.authorization_expiration_expected_at
            ),
            current_balance=domain_ibanity_account.current_balance,
            available_balance=domain_ibanity_account.available_balance,
            subtype=domain_ibanity_account.subtype,
            holder_name=domain_ibanity_account.holder_name,
            resource_id=domain_ibanity_account.resource_id,
        )

    def save(
        self, domain_ibanity_account: DomainIbanityAccount
    ) -> DomainIbanityAccount:
        """Save a IbanityAccount to the database."""
        # come back to this later
        db_ibanity_account = self._to_django(domain_ibanity_account)
        db_ibanity_account.save()
        return self._to_domain(db_ibanity_account)

    def get_or_create(self, user, account_id, data) -> Tuple[DomainIbanityAccount, bool]:
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
            Tuple[DomainIbanityAccount, bool]: (Account domain model, created flag)
        """
        ibanity_account, created = DjangoIbanityAccount.objects.get_or_create(
            user=user,
            account_id=account_id,
            defaults=data
        )

        return self._to_domain(ibanity_account), created

    def get_by_id(
        self, ibanity_account_id: int
    ) -> Optional[DomainIbanityAccount]:
        """Retrieve an IbanityAccount by its ID."""
        try:
            db_ibanity_account = DjangoIbanityAccount.objects.get(
                id=ibanity_account_id
            )
            return self._to_domain(db_ibanity_account)
        except ObjectDoesNotExist:
            return None

    def get_by_account_id(
        self, account_id: str
    ) -> Optional[DomainIbanityAccount]:
        """Retrieve an IbanityAccount by its account ID.
        """
        logger.debug(
            f"Searching for IbanityAccount with Account ID: "
            f"{account_id}"
        )
        logger.debug(f"Type of account ID: {account_id}")
        try:
            # Order by created_at descending and get the first one
            db_ibanity_account = DjangoIbanityAccount.objects.filter(
                account_id=account_id
            ).order_by('-created_at').first()

            if db_ibanity_account:
                logger.debug(
                    f"Found IbanityAccount in DB: "
                    f"{db_ibanity_account}"
                )
                return self._to_domain(db_ibanity_account)
            else:
                logger.debug("No IbanityAccount found with that account ID")
                return None

        except Exception as e:
            logger.error(f"Error retrieving IbanityAccount: {str(e)}")
            return None

    def get_by_user(self, user) -> Optional[DomainIbanityAccount]:
        """Retrieve an IbanityAccount by its user.
        """
        logger.debug(f"Searching for IbanityAccount of User: {user}")
        logger.debug(f"Type of user: {user}")
        try:
            # Order by created_at descending and get the first one
            db_ibanity_account = DjangoIbanityAccount.objects.filter(
                user=user
            ).first()

            if db_ibanity_account:
                logger.debug(
                    f"Found IbanityAccount in DB: "
                    f"{db_ibanity_account}"
                )
                return self._to_domain(db_ibanity_account)
            else:
                logger.debug("No IbanityAccount found of that user")
                return None

        except Exception as e:
            logger.error(f"Error retrieving IbanityAccount: {str(e)}")
            return None

    def update(
        self, domain_ibanity_account: DomainIbanityAccount, user
    ) -> DomainIbanityAccount:
        """Update an existing IbanityAccount.

        Args:
            domain_ibanity_account: Domain IbanityAccount with updated data
            user: User instance performing the update

        Returns:
            DomainIbanityAccount: Updated domain IbanityAccount

        Raises:
            InvalidIbanityAccountError: If IbanityAccount doesn't exist
        """
        try:
            db_ibanity_account = DjangoIbanityAccount.objects.get(
                user=user
            )

            db_ibanity_account.user = domain_ibanity_account.user
            db_ibanity_account.account_id = domain_ibanity_account.account_id
            db_ibanity_account.description = domain_ibanity_account.description
            db_ibanity_account.product = domain_ibanity_account.product
            db_ibanity_account.reference = domain_ibanity_account.reference
            db_ibanity_account.currency = domain_ibanity_account.currency
            db_ibanity_account.authorization_expiration_expected_at = (
                domain_ibanity_account.authorization_expiration_expected_at
            )
            db_ibanity_account.current_balance = domain_ibanity_account.current_balance
            db_ibanity_account.available_balance = domain_ibanity_account.available_balance
            db_ibanity_account.subtype = domain_ibanity_account.subtype
            db_ibanity_account.holder_name = domain_ibanity_account.holder_name
            db_ibanity_account.resource_id = domain_ibanity_account.resource_id

            # Save the changes to the database
            db_ibanity_account.save()
            return self._to_domain(db_ibanity_account)
        except ObjectDoesNotExist as exc:
            raise InvalidIbanityAccountError(
                f"IbanityAccount {domain_ibanity_account.account_id} not found"
            ) from exc

    def update_by_account_id(
        self, account_id: str, data
    ) -> DomainIbanityAccount:
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
        try:
            ibanity_account = DjangoIbanityAccount.objects.get(
                account_id=account_id
            )

            field_mapping = {
                'description': 'description',
                'product': 'product',
                'reference': 'reference',
                'currency': 'currency',
                'authorization_expiration_expected_at': (
                    'authorization_expiration_expected_at'
                ),
                'current_balance': 'current_balance',
                'available_balance': 'available_balance',
                'subtype': 'subtype',
                'holder_name': 'holder_name',
                'resource_id': 'resource_id'
            }

            # Update account fields
            for data_field, model_field in field_mapping.items():
                setattr(ibanity_account, model_field, data[data_field])

            ibanity_account.save()
            return self._to_domain(ibanity_account)
        except ObjectDoesNotExist as exc:
            raise InvalidIbanityAccountError(
                f"IbanityAccount with account ID {account_id} not found"
            ) from exc
        except Exception as e:
            raise InvalidIbanityAccountError(
                f"Error while updating IbanityAccount: {str(e)}"
            ) from e

    def process_accounts_data(
        self,
        user: Any,
        accounts_data: Dict[str, Any]
    ) -> DomainIbanityAccount:
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
        # Validate the account data
        account_info = self._validate_account_data(accounts_data)

        # Transform API data to domain model format
        account_data = self._transform_to_account_data(account_info)

        # Create or update the account
        account, created = self.get_or_create(
            user=user,
            account_id=account_info['id'],
            data=account_data
        )

        if not created:
            account = self.update_by_account_id(
                account_id=account_info['id'],
                data=account_data
            )

        return account

    def _validate_account_data(
        self, accounts_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the account data from Ponto API.

        Args:
            accounts_data: Raw account data from Ponto API

        Returns:
            Dict: The validated account data

        Raises:
            IbanityAccountDataError: If the account data is invalid
        """
        # Check if there are any accounts in the data
        data_empty = (
            not accounts_data.get('data') or
            len(accounts_data['data']) == 0
        )
        if data_empty:
            raise IbanityAccountDataError("No account data available")

        # Validate account data structure
        account_info = accounts_data['data'][0]
        if 'id' not in account_info:
            raise IbanityAccountDataError("Missing account ID in data")

        if 'attributes' not in account_info:
            raise IbanityAccountDataError(
                "Missing attributes in account data"
            )

        attributes = account_info['attributes']
        required_attrs = [
            'description', 'product', 'reference', 'currency',
            'authorizationExpirationExpectedAt', 'currentBalance',
            'availableBalance', 'subtype', 'holderName'
        ]

        missing_attrs = [
            attr for attr in required_attrs
            if attr not in attributes
        ]
        if missing_attrs:
            raise IbanityAccountDataError(
                f"Missing required attributes: {', '.join(missing_attrs)}"
            )

        # Store the nested path for clarity
        latest_sync = account_info['meta'].get('latestSynchronization', {})

        meta_missing = (
            'meta' not in account_info or
            'latestSynchronization' not in account_info['meta'] or
            'attributes' not in latest_sync or
            'resourceId' not in latest_sync.get('attributes', {})
        )
        if meta_missing:
            raise IbanityAccountDataError(
                "Missing resourceId in account data"
            )

        return account_info

    def _transform_to_account_data(
        self, account_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform the validated API data into domain model format.

        Args:
            account_info: Validated account info from Ponto API

        Returns:
            Dict: Data ready for domain model creation/update
        """
        return {
            'description': account_info['attributes']['description'],
            'product': account_info['attributes']['product'],
            'reference': account_info['attributes']['reference'],
            'currency': account_info['attributes']['currency'],
            'authorization_expiration_expected_at': (
                account_info['attributes']['authorizationExpirationExpectedAt']
            ),
            'current_balance': account_info['attributes']['currentBalance'],
            'available_balance': (
                account_info['attributes']['availableBalance']
            ),
            'subtype': account_info['attributes']['subtype'],
            'holder_name': account_info['attributes']['holderName'],
            'resource_id': (
                account_info['meta']
                ['latestSynchronization']
                ['attributes']
                ['resourceId']
            )
        }


class DjangoPontoTokenRepository(PontoTokenRepository):
    """Django ORM implementation of the PontoToken repository."""

    def _to_domain(self, db_ponto_token: DjangoPontoToken) -> DomainPontoToken:
        """Convert Django model to domain model.

        This method is used:
        1. When fetching data from the database
        2. Before returning data to business logic layer

        What it does:
        1. Takes database fields and maps them to domain model attributes
        2. Preserves the database ID for future reference
        3. Ensures data is in the format our domain logic expects

        Note:
            The `id` field is automatically provided by Django's ORM.
            Every Django model gets an auto-incrementing integer primary key
            field named 'id' unless explicitly specified otherwise.

        Args:
            db_ponto_token: Django ORM PontoToken model instance

        Returns:
            DomainPontoToken: Domain model populated with database values

        Example:
            # When fetching by ID:
            db_ponto_token = DjangoPontoToken.objects.get(id=123)
            domain_ponto_token = self._to_domain(db_ponto_token)
            return domain_ponto_token  # Ready for business logic
        """
        logger.debug(
            "Converting DB PontoToken to domain model: %s",
            db_ponto_token
        )
        # All Django models have an id field by default
        pontoToken_args = {
            'user': db_ponto_token.user,
            'access_token': db_ponto_token.access_token,
            'refresh_token': db_ponto_token.refresh_token,
            'expires_in': db_ponto_token.expires_in,
            # Map Django's auto-generated id to domain model's
            # pontoToken_id parameter. Domain model stores it as self.id
            'pontoToken_id': db_ponto_token.id  # type:ignore
        }
        logger.debug("Created PontoToken args: %s", pontoToken_args)

        return DomainPontoToken(**pontoToken_args)

    def _to_django(
        self,
        domain_ponto_token: DomainPontoToken,
        user
    ) -> DjangoPontoToken:
        """Convert domain model to Django model.

        This method is used:
        1. When saving new PontoTokens to database
        2. When updating existing PontoTokens

        What it does:
        1. Takes domain model attributes and maps them to database fields
        2. Adds necessary database-specific information (like user)
        3. Prepares data for database storage

        Args:
            domain_ponto_token: Domain model instance to convert
            user: User instance who owns this PontoToken

        Returns:
            DjangoPontoToken: Django ORM model ready for database operations

        Example:
            # When saving a new PontoToken:
            db_ponto_token = self._to_django(domain_ponto_token, user)
            db_ponto_token.save()
            return self._to_domain(db_ponto_token)
        """

        return DjangoPontoToken(
            user=domain_ponto_token.user,
            access_token=domain_ponto_token.access_token,
            refresh_token=domain_ponto_token.refresh_token,
            expires_in=domain_ponto_token.expires_in,
        )

    def save(
        self, domain_ponto_token: DomainPontoToken, user
    ) -> DomainPontoToken:
        """Save a PontoToken to the database."""
        # come back to this later
        db_ponto_token = self._to_django(domain_ponto_token, user)
        db_ponto_token.save()
        return self._to_domain(db_ponto_token)

    def get_by_id(self, pontoToken_id: int) -> Optional[DomainPontoToken]:
        """Retrieve an PontoToken by its ID."""
        try:
            db_ponto_token = DjangoPontoToken.objects.filter(id=pontoToken_id).first()
            return self._to_domain(db_ponto_token)
        except ObjectDoesNotExist:
            return None

    def get_or_create_by_user(self, user, data) -> Tuple[DomainPontoToken, bool]:
        """Retrieve an PontoToken by its user.
        """
        logger.debug(f"Searching for PontoToken of User: {user}")
        logger.debug(f"Type of user: {user}")
        try:
            # Order by created_at descending and get the first one
            db_ponto_token, created = DjangoPontoToken.objects.get_or_create(
                user=user, defaults=data
            )

            if db_ponto_token:
                logger.debug(f"Found PontoToken in DB: {db_ponto_token}")
                return self._to_domain(db_ponto_token), created
            else:
                logger.debug("No PontoToken found of that user")
                return None, None

        except Exception as e:
            logger.error(f"Error retrieving PontoToken: {str(e)}")
            return None

    def update_by_user(self, user, data) -> DomainPontoToken:
        """Update an existing PontoToken.

        Args:
            user (User): User instance performing the update
            data (dict): A dictionary containing the following keys:
                - access_token (str): The access token.
                - refresh_token (str): The refresh token.
                - expires_in (int): The expiration time in seconds.

        Returns:
            DomainPontoToken: Updated domain PontoToken

        Raises:
            InvalidPontoTokenError: If PontoToken doesn't exist
        """
        try:
            db_ponto_token = DjangoPontoToken.objects.filter(
                user=user
            ).first()

            # Use model's update method for encapsulation
            db_ponto_token.access_token = data['access_token']
            db_ponto_token.refresh_token = data['refresh_token']
            db_ponto_token.expires_in = data['expires_in']
            # Save the changes to the database
            db_ponto_token.save()
            return self._to_domain(db_ponto_token)
        except ObjectDoesNotExist as exc:
            raise InvalidPontoTokenError(
                f"PontoToken {DomainPontoToken.user} not found"
            ) from exc

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
        from integrations.providers.ponto import PontoProvider

        try:
            ponto_token = self.get_by_user(user=user)
            if ponto_token is None:
                raise PontoTokenNotFoundError(f"No token found for user {user}")
            return PontoProvider.decrypt_token(ponto_token.access_token)
        except ObjectDoesNotExist:
            raise PontoTokenNotFoundError(f"No token found for user {user}")
        except Exception as e:
            raise PontoTokenDecryptionError(
                f"Error decrypting token: {str(e)}"
            )
