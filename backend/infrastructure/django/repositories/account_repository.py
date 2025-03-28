from typing import Optional
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from domain.models.account import Account
from domain.repositories.interfaces.account_repository import AccountRepository

User = get_user_model()


class DjangoAccountRepository(AccountRepository):
    """Django implementation of the account repository."""

    def _to_domain(self, user) -> Optional[Account]:
        """Convert Django user model to domain Account."""
        if not user:
            return None
        return Account(
            id=user.id,
            username=user.username,
            email=user.email,
            company_name=user.company_name,
            is_active=user.is_active,
            first_name=user.first_name,
            last_name=user.last_name
        )

    def _prepare_password(self, password: str) -> str:
        """Hash password using Django's password hasher."""
        return make_password(password)

    def find_by_id(self, id: int) -> Optional[Account]:
        """Find account by ID."""
        try:
            user = User.objects.get(id=id)
            return self._to_domain(user)
        except User.DoesNotExist:
            return None

    def find_by_username(self, username: str) -> Optional[Account]:
        """Find account by username."""
        try:
            user = User.objects.get(username=username)
            return self._to_domain(user)
        except User.DoesNotExist:
            return None

    def find_by_email(self, email: str) -> Optional[Account]:
        """Find account by email."""
        try:
            user = User.objects.get(email=email)
            return self._to_domain(user)
        except User.DoesNotExist:
            return None

    def save(self, account: Account) -> Account:
        """Save account (create or update)."""
        user_data = {
            "username": account.username,
            "email": account.email,
            "company_name": account.company_name,
            "is_active": account.is_active,
            "first_name": account.first_name,
            "last_name": account.last_name,
        }

        if account._password:
            user_data["password"] = self._prepare_password(account._password)

        if account.id:
            # Update existing user
            try:
                user = User.objects.get(id=account.id)
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
                return self._to_domain(user)
            except User.DoesNotExist:
                raise ValueError(f"User with id {account.id} not found")
        else:
            # Create new user
            if not account._password:
                raise ValueError("Password is required for new accounts")
            
            user = User.objects.create(**user_data)
            return self._to_domain(user)

    def authenticate(self, username: str, password: str) -> Optional[Account]:
        """Authenticate user with username/email and password."""
        # Try with username
        user = authenticate(username=username, password=password)
        
        # If authentication with username fails, try with email
        if not user and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return None
                
        return self._to_domain(user)
