import os
import logging
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

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

# Get encryption key function
def get_encryption_key() -> bytes:
    """Get the encryption key from environment variables.
    
    Returns:
        bytes: The encryption key as bytes.
        
    Raises:
        ValueError: If the FERNET_KEY is not set in the environment.
        ValueError: If the FERNET_KEY is not a valid Fernet key.
    """
    key = os.getenv('FERNET_KEY')
    if key is None:
        logger.error("FERNET_KEY not found in the .env file!")
        raise ValueError("FERNET_KEY not found in the .env file!")
    
    # Ensure the key is valid (it should be a byte string)
    if isinstance(key, str):
        key = key.encode()
    elif not isinstance(key, bytes):
        logger.error("FERNET_KEY must be a string or bytes!")
        raise ValueError("FERNET_KEY must be a string or bytes!")
    
    # Validate key format (should be 32 bytes when decoded from url-safe base64)
    try:
        Fernet(key)
    except Exception as e:
        logger.error(f"FERNET_KEY is not a valid Fernet key: {str(e)}")
        raise ValueError("FERNET_KEY is not a valid Fernet key. It must be URL-safe base64-encoded 32-byte key.") from e
    
    return key

# Encryption function
def encrypt_token(token: str, key: bytes) -> str:
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
        fernet = Fernet(key)
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
def decrypt_token(encrypted_token: str, key: bytes) -> str:
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
        fernet = Fernet(key)
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
