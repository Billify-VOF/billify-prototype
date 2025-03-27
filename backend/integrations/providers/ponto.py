import logging
import secrets
import base64
import ssl
import certifi
import urllib3

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from config.settings.base import (
    FERNET_KEY,
    PONTO_CERTIFICATE_PATH,
    PONTO_PRIVATE_KEY_PATH,
    PONTO_PRIVATE_KEY_PASSWORD,
    IBANITY_API_HOST,
)

# Initialize logger
logger = logging.getLogger(__name__)


def is_empty(text: str) -> bool:
    """Check if a string is None, empty, or contains only whitespace."""
    if text is None:
        return True
    has_no_content = not text.strip()
    return has_no_content


class PontoProvider:
    """Provide utils functions like encrypt, decrypt for integration with Ponto"""

    @staticmethod
    def encrypt_token(token: str) -> str:
        """Encrypt a token using Fernet symmetric encryption.

        Args:
            token (str): The token to encrypt.

        Returns:
            str: The encrypted token as a string.

        Raises:
            ValueError: If the token is empty or the key is invalid.
            cryptography.fernet.InvalidToken: If the token cannot be encrypted.
            TypeError: If there's a type mismatch in the inputs.
        """
        try:
            if is_empty(token):
                raise ValueError("Invalid token: Token cannot be empty or whitespace.")
            fernet = Fernet(FERNET_KEY)
            encrypted_token = fernet.encrypt(token.encode())
            logger.debug("Token successfully encrypted.")
            return encrypted_token.decode()

        except ValueError as ve:
            logger.error(f"Invalid input provided for encryption: {str(ve)}")
            raise ValueError(f"Invalid input for encryption: {str(ve)}") from ve
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise RuntimeError("An unexpected error occurred while encrypting token.") from e

    @staticmethod
    def decrypt_token(encrypted_token: str) -> str:
        """Decrypt an encrypted token using Fernet symmetric encryption.

        Args:
            encrypted_token (str): The encrypted token to decrypt.

        Returns:
            str: The decrypted token as a string.

        Raises:
            InvalidToken: If the encrypted token is invalid.
            ValueError: If the encrypted token is empty or the key is invalid.
            TypeError: If there's a type mismatch in the inputs.
        """
        try:
            if is_empty(encrypted_token):
                raise ValueError("Invalid token: Token cannot be empty or whitespace.")
            fernet = Fernet(FERNET_KEY)
            decrypted_token = fernet.decrypt(encrypted_token.encode())
            logger.info("Token successfully decrypted.")
            return decrypted_token.decode()

        except InvalidToken as it:
            logger.error(f"Invalid token provided for decryption: {str(it)}")
            raise InvalidToken("The encrypted token is invalid or corrupted.") from it

        except ValueError as ve:
            if "Invalid token" in str(ve):
                logger.error(f"Invalid token for decryption: {str(ve)}")
                raise
            else:
                logger.error(f"Invalid key provided for decryption: {str(ve)}")
                raise ValueError("The decryption key provided is invalid.") from ve

        except TypeError as te:
            logger.error(f"Type error during decryption: {str(te)}")
            raise TypeError(f"Type error during decryption: {str(te)}") from te
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise RuntimeError("An unexpected error occurred while decrypting token.") from e

    @staticmethod
    def generate_client_credentials(client_id: str, client_secret: str) -> str:
        """Convert client ID and secret to a Base64-encoded string in format 'client_id:client_secret'.

        Concatenate client_id and client_secret with a colon.

        Used for HTTP Basic Authentication in API requests.

        Args:
            client_id (str): The client ID.
            client_secret (str): The client secret.

        Returns:
            str: Base64-encoded client credentials.

        Raises:
            ValueError: If inputs are empty or encoding fails.
        """
        if is_empty(client_id) or is_empty(client_secret):
            raise ValueError("Client ID and secret cannot be empty or whitespace.")
        try:
            client_credentials = f"{client_id}:{client_secret}"
            credentials_bytes = client_credentials.encode("utf-8")
            base64_bytes = base64.b64encode(credentials_bytes)
            encoded_credentials = base64_bytes.decode("utf-8")
            return encoded_credentials
        except (UnicodeError, TypeError) as e:
            logger.error(f"Error encoding credentials: {str(e)}")
            raise ValueError(f"Failed to encode credentials: {str(e)}") from e

    @staticmethod
    def generate_random_session_id(prefix="session_", length=50) -> str:
        """Generate a random session ID.

        Args:
            prefix (str): The prefix to use for the session ID. Default is "session_".
            length (int): The length of the random string to generate. Default is 50.

        Returns:
            str: A secure random alphanumeric string that has length characters.

        Raises:
            ValueError: If length is less than 1.
        """
        try:
            if length < 1:
                raise ValueError("Length must be at least 1.")

            random_string = secrets.token_urlsafe(length)
            logger.info(f"Generated session id: {prefix}{random_string}")
            return f"{prefix}{random_string}"

        except Exception as e:
            logging.error(f"Error generating session ID: {e}")
            return ""

    @staticmethod
    def create_signature(request_target: str, digest: str, created: str) -> str:
        """Creates the signature string.

        Args:
            request_target (str): The request target.
            digest (str): The digest value.
            created (str): The created timestamp.

        Returns:
            str: The generated signature.

        Raises:
            IOError: If the private key file cannot be read.
            ValueError: If the private key is invalid or the signature cannot be created.
        """
        if not request_target or not digest:
            raise ValueError("Required parameters cannot be empty")

        signing_string = f"""(request-target): {request_target}\ndigest: {digest}\n(created): {created}\nhost: {IBANITY_API_HOST}"""

        try:
            # Load the private key with the password
            with open(PONTO_PRIVATE_KEY_PATH, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(), password=PONTO_PRIVATE_KEY_PASSWORD.encode(), backend=default_backend()
                )

            # Sign the message
            signature_bytes = private_key.sign(
                signing_string.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256()
            )

            # Base64 encode the signature
            signature = base64.b64encode(signature_bytes).decode("utf-8")

            return signature
        except IOError as e:
            logger.error(f"Failed to read private key file: {e}")
            raise IOError(f"Failed to read private key file: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid private key or password: {e}")
            raise ValueError(f"Invalid private key or password: {e}") from e
        except Exception as e:
            logger.error(f"Failed to create signature: {e}")
            raise

    @staticmethod
    def create_http_instance():
        """Create and configure an HTTPS connection instance using SSL.

        This method sets up an SSL context for secure communications with
        the specified certificate and private key files. It also creates
        a PoolManager instance with the configured SSL context to manage
        HTTP connection pooling efficiently.

        Returns:
            urllib3.PoolManager: A configured PoolManager instance for making
            HTTPS requests.

        Raises:
            RuntimeError: If there is any issue with loading the SSL certificate
            or key files, or if there is a failure in configuring the SSL
            context.
            FileNotFoundError: If the specified certificate or private key files
            cannot be found.
            ssl.SSLError: If there is a problem with the SSL configuration,
            such as invalid certificates.

        Example:
            http_instance = PontoProvider.create_http_instance()
            response = http_instance.request('GET', 'https://example.com')
        """
        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.load_cert_chain(
                certfile=PONTO_CERTIFICATE_PATH,
                keyfile=PONTO_PRIVATE_KEY_PATH,
                password=PONTO_PRIVATE_KEY_PASSWORD,
            )

            # Create a PoolManager with the SSL context
            http = urllib3.PoolManager(
                num_pools=50, cert_reqs=ssl.CERT_REQUIRED, ca_certs=certifi.where(), ssl_context=context
            )
        except FileNotFoundError as e:
            logger.error(f"Certificate or key file not found: {e}")
            raise RuntimeError("Failed to load SSL certificate or key.") from e
        except ssl.SSLError as e:
            logger.error(f"SSL error occurred: {e}")
            raise RuntimeError("SSL configuration failed.") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise RuntimeError("An unexpected error occurred while creating HTTP instance.") from e

        return http
