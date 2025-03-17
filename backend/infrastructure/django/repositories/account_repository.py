from typing import Optional
from django.contrib.auth import authenticate as django_authenticate, get_user_model
from domain.models.account import Account
from domain.repositories.interfaces.account_repository import AccountRepository

User = get_user_model()


def _to_domain(user_model) -> Optional[Account]:
    """Convert Django User model to domain Account entity."""
    if not user_model:
        return None

    return Account(
        id=user_model.id,
        username=user_model.username,
        email=user_model.email,
        password=None,
        is_active=user_model.is_active,
        first_name=user_model.first_name,
        last_name=user_model.last_name
    )


class DjangoAccountRepository(AccountRepository):
    """Django implementation of the AccountRepository interface."""

    def find_by_id(self, id: int) -> Optional[Account]:
        try:
            user = User.objects.get(id=id)
            return _to_domain(user)
        except User.DoesNotExist:
            return None

    def find_by_username(self, username: str) -> Optional[Account]:
        try:
            user = User.objects.get(username=username)
            return _to_domain(user)
        except User.DoesNotExist:
            return None

    def find_by_email(self, email: str) -> Optional[Account]:
        try:
            user = User.objects.get(email=email)
            return _to_domain(user)
        except User.DoesNotExist:
            return None

    def save(self, account: Account) -> Account:
        """Save account (create or update)."""
        user, created = User.objects.update_or_create(
            id=account.id,
            defaults={
                "username": account.username,
                "email": account.email,
                "is_active": account.is_active,
                "first_name": account.first_name,
                "last_name": account.last_name,
            },
        )
        return _to_domain(user)

    def authenticate(self, username: str, password: str) -> Optional[Account]:
        user = django_authenticate(username=username, password=password)
        return _to_domain(user)
