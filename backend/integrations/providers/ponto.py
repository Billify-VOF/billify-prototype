import logging
import secrets
import base64
import string

from cryptography.fernet import Fernet, InvalidToken
from OpenSSL import crypto

from config.settings.base import PONTO_CONNECT_BASE_URL, \
    PONTO_PRIVATE_KEY_PASSWORD, PONTO_SIGNATURE_KEY_ID, FERNET_KEY, \
    PONTO_CERTIFICATE_PATH, PONTO_PRIVATE_KEY_PATH

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


class PontoProvider():
  """Provide utils functions like encrypt, decrypt for integration with Ponto"""

  # Encryption function
  @staticmethod
  def encrypt_token(token: str) -> str:
      """Encrypt a token using Fernet symmetric encryption.
      
      Args:
          token (str): The token to encrypt.
          key (bytes): The encryption key.
          
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
          key (bytes): The decryption key.
          
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
  def generate_random_session_id() -> str:
      """Generate a random session ID.
      
      Returns:
          str: A randomly generated session ID.
      """
      random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50))  # Generate a secure random 50-character alphanumeric string
      return f"session_{random_string}"

  @staticmethod
  def load_private_key(private_key_path: str, password: str):
      """Load and decrypt a private key from a file.
      
      Args:
          private_key_path (str): Path to the private key file.
          password (str): Password to decrypt the private key.
          
      Returns:
          object: The loaded private key.
          
      Raises:
          IOError: If the private key file cannot be read.
          crypto.Error: If the private key cannot be decrypted with the given password.
      """
      try:
          # Read and load the private key
          with open(private_key_path, 'rb') as key_file:
              private_key_data = key_file.read()
          try:
              # Decrypt the private key with the provided password
              private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, passphrase=password.encode())
              return private_key
          except crypto.Error as e:
              logger.error(f"Failed to decrypt private key: {str(e)}")
              raise crypto.Error(f"Failed to decrypt private key: {str(e)}") from e
      except IOError as e:
          logger.error(f"Failed to read private key file: {str(e)}")
          raise IOError(f"Failed to read private key file: {str(e)}") from e

  @staticmethod
  def create_signature(request_target: str, digest: str, created: str, private_key_path: str, private_key_password: str) -> str:
      """Creates the signature string.
      
      Args:
          request_target (str): The request target.
          digest (str): The digest value.
          created (str): The created timestamp.
          private_key_path (str): Path to the private key file.
          private_key_password (str): Password for the private key.
          
      Returns:
          str: The generated signature.
          
      Raises:
          IOError: If the private key file cannot be read.
          ValueError: If the private key is invalid or the signature cannot be created.
      """
      signing_string = f"""(request-target): {request_target}\ndigest: {digest}\n(created): {created}\nhost: api.ibanity.com"""
      
      try:
          # Load the private key with the password
          with open(private_key_path, "rb") as key_file:
              private_key = serialization.load_pem_private_key(
                  key_file.read(),
                  password=private_key_password.encode(),
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
          raise ValueError(f"Failed to create signature: {e}") from e
