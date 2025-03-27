from domain.services.token_encryption_service import TokenEncryptionService
from integrations.providers.ponto import PontoProvider


class PontoTokenEncryptionService(TokenEncryptionService):
    """
    Service for encrypting and decrypting tokens using the PontoProvider.

    This class implements the `TokenEncryptionService` abstract base class,
    providing specific encryption and decryption methods utilizing the
    functionalities of the `PontoProvider`. The service is designed
    to handle sensitive token operations securely by leveraging
    the capabilities offered by the Ponto integration.

    Methods:
        encrypt(token: str) -> str:
            Encrypts the given plain token and returns the encrypted version.

        decrypt(encrypted_token: str) -> str
            Decrypts the provided encrypted token and returns the original plain token.

    Example:
        service = PontoTokenEncryptionService()

        # Encrypting a token
        original_token = "my_secret_token"
        encrypted = service.encrypt(original_token)
        print(f"Encrypted Token: {encrypted}")  # Outputs the encrypted token

        # Decrypting a token
        decrypted = service.decrypt(encrypted)
        print(f"Decrypted Token: {decrypted}")  # Outputs the original token
    """

    def encrypt(self, token: str) -> str:
        """
        Encrypts the given token using the PontoProvider's encryption method.

        This method takes a plain token and returns its encrypted representation.
        It utilizes the `encrypt_token` method from the `PontoProvider`
        to ensure that the token is securely encrypted before storage or transmission.

        Args:
            token (str): The plain text token to be encrypted.

        Returns:
            str: The encrypted token as a string.
        """
        return PontoProvider.encrypt_token(token)

    def decrypt(self, encrypted_token: str) -> str:
        """
        Decrypts the given encrypted token using the PontoProvider's decryption method.

        This method takes an encrypted token and returns its original plain text
        representation. It leverages the `decrypt_token` method from the `PontoProvider`
        to decrypt the token securely.

        Args:
            encrypted_token (str): The encrypted token to be decrypted.

        Returns:
            str: The original plain text token.
        """
        return PontoProvider.decrypt_token(encrypted_token)
