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

from config.settings.base import FERNET_KEY, PONTO_CERTIFICATE_PATH, \
                          PONTO_PRIVATE_KEY_PATH, PONTO_PRIVATE_KEY_PASSWORD, \
                          IBANITY_API_HOST

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

# Create a console handler and set the logging level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and attach it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)


class PontoProvider:
  """Provide utils functions like encrypt, decrypt for integration with Ponto"""

  # Encryption function
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
          if not token or not token.strip():
              raise ValueError("Invalid token: Token cannot be empty or whitespace.")
          fernet = Fernet(FERNET_KEY)
          encrypted_token = fernet.encrypt(token.encode())  # Convert the token to bytes before encryption
          logger.debug("Token successfully encrypted.")
          return encrypted_token.decode()  # Return the encrypted token as a string
      
      except ValueError as ve:
          logger.error(f"Invalid input provided for encryption: {str(ve)}")
          raise ValueError(f"Invalid input for encryption: {str(ve)}") from ve
      
      except Exception as e:
          logger.error(f"Error while encrypting token: {str(e)}")
          raise Exception(f"Error while encrypting token: {str(e)}") from e

  # Decryption function
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
          if not encrypted_token or not encrypted_token.strip():
              raise ValueError("Invalid token: Token cannot be empty or whitespace.")
          fernet = Fernet(FERNET_KEY)
          decrypted_token = fernet.decrypt(encrypted_token.encode())  # Convert the encrypted token back to bytes
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

  @staticmethod
  def generate_client_credentials(client_id: str, client_secret: str) -> str:
      """Convert client ID and secret to a Base64-encoded string.
      
      Args:
          client_id (str): The client ID.
          client_secret (str): The client secret.
          
      Returns:
          str: Base64-encoded client credentials.
      """
      # Concatenate client_id and client_secret with a colon
      client_credentials = f"{client_id}:{client_secret}"
      encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')
      return encoded_credentials

  @staticmethod
  def generate_random_session_id(prefix="session_", length=50) -> str:
      """Generate a random session ID.
      
      Returns:
          str: A secure random alphanumeric string that has length characters.
      """
      random_string = secrets.token_urlsafe(length)
      return f"{prefix}{random_string}"

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
                  key_file.read(),
                  password=PONTO_PRIVATE_KEY_PASSWORD.encode(),
                  backend=default_backend()
              )

          # Sign the message
          signature_bytes = private_key.sign(
              signing_string.encode('utf-8'),
              padding.PKCS1v15(),
              hashes.SHA256()
          )

          # Base64 encode the signature
          signature = base64.b64encode(signature_bytes).decode('utf-8')

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
    """Create and configure an SSL context."""
    try:
        context = ssl.create_default_context()
        context.check_hostname = True
        context.load_cert_chain(
            certfile=PONTO_CERTIFICATE_PATH,
            keyfile=PONTO_PRIVATE_KEY_PATH,
            password=PONTO_PRIVATE_KEY_PASSWORD
        )

        # Create a PoolManager with the SSL context
        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_REQUIRED,  
            ca_certs=certifi.where(),
            ssl_context=context
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
