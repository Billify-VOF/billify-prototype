"""Custom exceptions for the domain.

These exceptions represent different types of failures that can occur
during invoice processing or Ponto interaction, helping us handle
errors appropriately at different layers of the application.
"""


class InvoiceError(Exception):
    """Base exception class for all invoice-related errors.

    All other invoice exceptions inherit from this class, allowing
    for catch-all handling of invoice-specific errors when needed.
    """


class InvalidInvoiceError(InvoiceError):
    """Raised when an invoice fails business rule validation.

    This could be due to issues like missing required fields,
    invalid data formats, or other business rule violations.
    """


class StorageError(InvoiceError):
    """Raised when there are problems storing invoice files.

    This covers issues like storage unavailability, permission
    problems, or other file system related errors.
    """


class ProcessingError(InvoiceError):
    """Raised when invoice processing fails for business logic reasons.

    This could be due to issues like data extraction failures,
    validation problems, or other processing-related errors.
    """


class IbanityAccountError(Exception):
    """Base exception class for all Ibanity account-related errors.

    All other Ibanity account exceptions inherit from this class, allowing
    for catch-all handling of Ibanity account-specific errors when needed.
    """


class InvalidIbanityAccountError(IbanityAccountError):
    """Raised when an Ibanity account fails business rule validation.

    This could be due to issues like missing required fields,
    invalid data formats, or other business rule violations.
    """

class NegativeBalanceError(IbanityAccountError):
    """Raised when an account has a negative balance when not allowed.

    Example:
        try:
            account.validate()
        except NegativeBalanceError as e:
            logger.error(f"Balance validation failed: {e}")
            # Handle negative balance error (e.g., Re-fetch the account data)
    """


class ExpiredAuthorizationError(IbanityAccountError):
    """Raised when the account's authorization has expired.

    Example:
        try:
            account.validate()
        except ExpiredAuthorizationError as e:
            logger.error(f"Authorization expired: {e}")
            # Handle authorization error (e.g., Re-authentication)
    """


class InvalidCurrencyError(IbanityAccountError):
    """Raised when the account has an unsupported currency.

    Example:
        try:
            account.validate()
        except InvalidCurrencyError as e:
            logger.error(f"Currency not supported: {e}")
            # Handle currency error (e.g., show warning alert for currency error)
    """


class IbanityAccountNotFoundError(IbanityAccountError):
    """Raised when an Ibanity account is not found for a user."""


class IbanityAccountDataError(IbanityAccountError):
    """Raised when there are issues with Ibanity account data structure."""


class PontoTokenError(Exception):
    """Base exception class for all Ponto token-related errors.

    All other Ponto token exceptions inherit from this class, allowing
    for catch-all handling of Ponto token-specific errors when needed.
    """


class InvalidPontoTokenError(PontoTokenError):
    """Raised when a Ponto token fails business rule validation.

    This could be due to issues like missing required fields,
    invalid data formats, or other business rule violations.
    """


class PontoTokenNotFoundError(PontoTokenError):
    """Raised when a Ponto token is not found for a user."""


class PontoTokenDecryptionError(PontoTokenError):
    """Raised when there is an error decrypting a Ponto token."""


class PontoTokenCreationError(PontoTokenError):
    """Raised when there is an error creating or updating a Ponto token."""

    Example:
        try:
            token.validate()
        except InvalidPontoTokenError as e:
            logger.error(f"Token validation failed: {e}")
            # Handle token error (e.g., redirect to re-authentication)
    """


class PontoTokenExpirationError(PontoTokenError):
    """
    Exception raised when a Ponto API token has expired.

    This error indicates that an operation could not be completed because
    the provided token is no longer valid due to expiration.

    Usage:
        Raise this exception when the token is checked and found to
        be expired during an operation that requires a valid token.

    Example:
        try:
            token.validate()
        except PontoTokenExpirationError as e:
            logger.error(f"Token expired: {e}")
            # Handle token error (e.g., redirect to re-authentication)
    """  
