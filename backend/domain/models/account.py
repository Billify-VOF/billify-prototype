# Domain entity for Account
class Account:
    """Domain entity representing a user account in the system."""

    def __init__(
        self,
        id,
        username,
        email,
        company_name=None,
        password=None,
        is_active=True,
        first_name="",
        last_name="",
    ):
        self.id = id
        self.username = username
        self.email = email
        self.company_name = company_name
        self._password = password  # Not stored directly, used for authentication
        self.is_active = is_active
        self.first_name = first_name
        self.last_name = last_name

    def is_valid_for_authentication(self):
        """Check if account can be authenticated."""
        return self.is_active and self.email and self.username

    @property
    def full_name(self):
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
