"""Custom exceptions for the invoice processing domain.

These exceptions represent different types of failures that can occur
during invoice processing, helping us handle errors appropriately
at different layers of the application.
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


class PontoTokenError(Exception):
    """Base exception class for all Ponto token-related errors.

    All other Ponto token exceptions inherit from this class, allowing
    for catch-all handling of Ponto token-specific errors when needed.
    """


class InvalidPontoTokenError(PontoTokenError):
    """Raised when an Ponto token fails business rule validation.

    This could be due to issues like missing required fields,
    invalid data formats, or other business rule violations.
    """