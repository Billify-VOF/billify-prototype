"""Django ORM implementation of the Ponto-related repository interfaces."""

from typing import Optional, Dict, Any
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
        self, db_ibanityAccount: DjangoIbanityAccount
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
            db_ibanityAccount: Django ORM IbanityAccount model instance

        Returns:
            DomainIbanityAccount: Domain model populated with database values

        Example:
            # When fetching by ID:
            db_ibanityAccount = DjangoIbanityAccount.objects.get(id=123)
            domain_ibanityAccount = self._to_domain(db_ibanityAccount)
            return domain_ibanityAccount  # Ready for business logic
        """
        logger.debug(
            "Converting DB IbanityAccount to domain model: %s",
            db_ibanityAccount
        )
        # All Django models have an id field by default
        ibanityAccount_args = {
            'user': db_ibanityAccount.user,
            'account_id': db_ibanityAccount.account_id,
            'description': db_ibanityAccount.description,
            'product': db_ibanityAccount.product,
            'reference': db_ibanityAccount.reference,
            'currency': db_ibanityAccount.currency,
            'authorization_expiration_expected_at': (
                db_ibanityAccount.authorization_expiration_expected_at
            ),
            'current_balance': db_ibanityAccount.current_balance,
            'available_balance': db_ibanityAccount.available_balance,
            'subtype': db_ibanityAccount.subtype,
            'holder_name': db_ibanityAccount.holder_name,
            'resource_id': db_ibanityAccount.resource_id,
            # Map Django's auto-generated id to domain model's
            # ibanityAccount_id parameter. Domain model stores it as self.id
            'ibanityAccount_id': db_ibanityAccount.id  # type: ignore
        }

        return DomainIbanityAccount(**ibanityAccount_args)

    def _to_django(
        self,
        domain_ibanityAccount: DomainIbanityAccount,
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
            domain_ibanityAccount: Domain model instance to convert
            user: User instance who owns this IbanityAccount

        Returns:
            DjangoIbanityAccount: Django ORM model ready for
            database operations

        Example:
            # When saving a new IbanityAccount:
            db_ibanityAccount = self._to_django(domain_ibanityAccount, user)
            db_ibanityAccount.save()
            return self._to_domain(db_ibanityAccount)
        """

        return DjangoIbanityAccount(
            user=domain_ibanityAccount.user,
            account_id=domain_ibanityAccount.account_id,
            description=domain_ibanityAccount.description,
            product=domain_ibanityAccount.product,
            reference=domain_ibanityAccount.reference,
            currency=domain_ibanityAccount.currency,
            authorization_expiration_expected_at=(
                domain_ibanityAccount.authorization_expiration_expected_at
            ),
            current_balance=domain_ibanityAccount.current_balance,
            available_balance=domain_ibanityAccount.available_balance,
            subtype=domain_ibanityAccount.subtype,
            holder_name=domain_ibanityAccount.holder_name,
            resource_id=domain_ibanityAccount.resource_id,
        )

    def save(
        self, domainIbanityAccount: DomainIbanityAccount, user
    ) -> DomainIbanityAccount:
        """Save a IbanityAccount to the database."""
        # come back to this later
        db_ibanityAccount = self._to_django(domainIbanityAccount, user)
        db_ibanityAccount.save()
        return self._to_domain(db_ibanityAccount)

    def get_or_create(self, user, account_id, data) -> DomainIbanityAccount:
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
        """
        ibanityAccount, created = DjangoIbanityAccount.objects.get_or_create(
            user=user,
            account_id=account_id,
            defaults=data
        )

        return self._to_domain(ibanityAccount), created

    def get_by_id(
        self, ibanityAccount_id: int
    ) -> Optional[DomainIbanityAccount]:
        """Retrieve an IbanityAccount by its ID."""
        try:
            db_ibanityAccount = DjangoIbanityAccount.objects.get(
                id=ibanityAccount_id
            )
            return self._to_domain(db_ibanityAccount)
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
            db_ibanityAccount = DjangoIbanityAccount.objects.filter(
                account_id=account_id
            ).order_by('-created_at').first()

            if db_ibanityAccount:
                logger.debug(
                    f"Found IbanityAccount in DB: "
                    f"{db_ibanityAccount}"
                )
                return self._to_domain(db_ibanityAccount)
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
            db_ibanityAccount = DjangoIbanityAccount.objects.get(
                user=user
            )

            if db_ibanityAccount:
                logger.debug(
                    f"Found IbanityAccount in DB: "
                    f"{db_ibanityAccount}"
                )
                return self._to_domain(db_ibanityAccount)
            else:
                logger.debug("No IbanityAccount found of that user")
                return None

        except Exception as e:
            logger.error(f"Error retrieving IbanityAccount: {str(e)}")
            return None

    def update(
        self, domainIbanityAccount: DomainIbanityAccount, user
    ) -> DomainIbanityAccount:
        """Update an existing IbanityAccount.

        Args:
            domainIbanityAccount: Domain IbanityAccount with updated data
            user: User instance performing the update

        Returns:
            DomainIbanityAccount: Updated domain IbanityAccount

        Raises:
            InvalidIbanityAccountError: If IbanityAccount doesn't exist
        """
        try:
            db_ibanityAccount = DjangoIbanityAccount.objects.get(
                user=user
            )

            # Use model's update method for encapsulation
            db_ibanityAccount.update(
                user=domainIbanityAccount.user,
                account_id=domainIbanityAccount.account_id,
                description=domainIbanityAccount.description,
                product=domainIbanityAccount.product,
                reference=domainIbanityAccount.reference,
                currency=domainIbanityAccount.currency,
                authorization_expiration_expected_at=(
                    domainIbanityAccount.authorization_expiration_expected_at
                ),
                current_balance=domainIbanityAccount.current_balance,
                available_balance=domainIbanityAccount.available_balance,
                subtype=domainIbanityAccount.subtype,
                holder_name=domainIbanityAccount.holder_name,
                resource_id=domainIbanityAccount.resource_id,
            )
            # Save the changes to the database
            db_ibanityAccount.save()
            return self._to_domain(db_ibanityAccount)
        except ObjectDoesNotExist as exc:
            raise InvalidIbanityAccountError(
                f"IbanityAccount {domainIbanityAccount.account_id} not found"
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
            ibanityAccount = DjangoIbanityAccount.objects.get(
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
                setattr(ibanityAccount, model_field, data[data_field])

            ibanityAccount.save()
            return self._to_domain(ibanityAccount)
        except ObjectDoesNotExist as exc:
            raise InvalidIbanityAccountError(
                f"IbanityAccount with account ID {account_id} not found"
            ) from exc
        except Exception as e:
            raise InvalidPontoTokenError(
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

    def _to_domain(self, db_pontoToken: DjangoPontoToken) -> DomainPontoToken:
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
            db_pontoToken: Django ORM PontoToken model instance

        Returns:
            DomainPontoToken: Domain model populated with database values

        Example:
            # When fetching by ID:
            db_pontoToken = DjangoPontoToken.objects.get(id=123)
            domain_pontoToken = self._to_domain(db_pontoToken)
            return domain_pontoToken  # Ready for business logic
        """
        logger.debug(
            "Converting DB PontoToken to domain model: %s",
            db_pontoToken
        )
        # All Django models have an id field by default
        pontoToken_args = {
            'user': db_pontoToken.user,
            'access_token': db_pontoToken.access_token,
            'refresh_token': db_pontoToken.refresh_token,
            'expires_in': db_pontoToken.expires_in,
            # Map Django's auto-generated id to domain model's
            # pontoToken_id parameter. Domain model stores it as self.id
            'pontoToken_id': db_pontoToken.id  # type:ignore
        }
        logger.debug("Created PontoToken args: %s", pontoToken_args)

        return DomainPontoToken(**pontoToken_args)

    def _to_django(
        self,
        domain_pontoToken: DomainPontoToken,
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
            domain_pontoToken: Domain model instance to convert
            user: User instance who owns this PontoToken

        Returns:
            DjangoPontoToken: Django ORM model ready for database operations

        Example:
            # When saving a new PontoToken:
            db_PontoToken = self._to_django(domain_pontoToken, user)
            db_PontoToken.save()
            return self._to_domain(db_PontoToken)
        """

        return DjangoPontoToken(
            user=domain_pontoToken.user,
            access_token=domain_pontoToken.access_token,
            refresh_token=domain_pontoToken.refresh_token,
            expires_in=domain_pontoToken.expires_in,
        )

    def save(
        self, domainPontoToken: DomainPontoToken, user
    ) -> DomainPontoToken:
        """Save a PontoToken to the database."""
        # come back to this later
        db_PontoToken = self._to_django(domainPontoToken, user)
        db_PontoToken.save()
        return self._to_domain(db_PontoToken)

    def get_by_id(self, pontoToken_id: int) -> Optional[DomainPontoToken]:
        """Retrieve an PontoToken by its ID."""
        try:
            db_PontoToken = DjangoPontoToken.objects.get(id=pontoToken_id)
            return self._to_domain(db_PontoToken)
        except ObjectDoesNotExist:
            return None

    def get_or_create_by_user(self, user, data) -> Optional[DomainPontoToken]:
        """Retrieve an PontoToken by its user.
        """
        logger.debug(f"Searching for PontoToken of User: {user}")
        logger.debug(f"Type of user: {user}")
        try:
            # Order by created_at descending and get the first one
            db_PontoToken, created = DjangoPontoToken.objects.get_or_create(
                user=user, defaults=data
            ).order_by('-created_at').first()

            if db_PontoToken:
                logger.debug(f"Found PontoToken in DB: {db_PontoToken}")
                return self._to_domain(db_PontoToken), created
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
            db_PontoToken = DjangoPontoToken.objects.get(
                user=user
            )

            # Use model's update method for encapsulation
            db_PontoToken.access_token = data['access_token']
            db_PontoToken.refresh_token = data['refresh_token']
            db_PontoToken.expires_in = data['expires_in']
            # Save the changes to the database
            db_PontoToken.save()
            return self._to_domain(db_PontoToken)
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
            return PontoProvider.decrypt_token(ponto_token.access_token)
        except ObjectDoesNotExist:
            raise PontoTokenNotFoundError(f"No token found for user {user}")
        except Exception as e:
            raise PontoTokenDecryptionError(
                f"Error decrypting token: {str(e)}"
            )
