from abc import ABC, abstractmethod


class TokenEncryptionService(ABC):
    """
    Abstract base class for token encryption services.

    This class provides a blueprint for implementing encryption and
    decryption services for tokens. Any subclass must provide
    concrete implementations of the `encrypt` and `decrypt` methods.

    The purpose of this service is to ensure that sensitive tokens
    can be securely encrypted before storage or transmission, and
    decrypted when needed.

    Methods:
        encrypt: Takes a plain token as input and returns an encrypted version of it.
        decrypt: Takes an encrypted token as input and returns the original plain token.

    Example:
        class SimpleTokenEncryptionService(TokenEncryptionService):
            def encrypt(self, token: str) -> str:
                # Implement encryption logic here
                return encrypted_token

            def decrypt(self, encrypted_token: str) -> str:
                # Implement decryption logic here
                return plain_token

        service = SimpleTokenEncryptionService()
        encrypted = service.encrypt("my_secret_token")
        original = service.decrypt(encrypted)

    Raises:
        ValueError: If the input token is invalid during encryption or decryption.
    """

    @abstractmethod
    def encrypt(self, token: str) -> str:
        """Encrypt a token and return its encrypted form."""
        pass

    @abstractmethod
    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token and return the original token."""
        pass
