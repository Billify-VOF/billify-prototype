from cryptography.fernet import Fernet, InvalidToken
import os
import logging
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()


def get_encryption_key() -> bytes:
    """Get the encryption key from environment variables.
    
    Returns:
        bytes: The encryption key as bytes.
        
    Raises:
        ValueError: If the FERNET_KEY is not set in the environment.
    """
    key = os.getenv('FERNET_KEY')
    if key is None:
        raise ValueError("FERNET_KEY not found in the .env file!")
    
    # Ensure the key is valid (it should be a byte string)
    if isinstance(key, str):
        return key.encode()
    return key


def generate_key() -> bytes:
    """Generate a new Fernet key for encryption/decryption.
    
    Returns:
        bytes: A new Fernet key that can be stored in the .env file.
    """
    return Fernet.generate_key()


# Encryption function
def encrypt_token(token: str, key: bytes) -> str:
    """Encrypt a token using Fernet symmetric encryption.
    
    Args:
        token (str): The token to encrypt. Must not be empty and should be at least 8 characters.
        key (bytes): The Fernet key used for encryption. Must be a valid 32-byte key encoded in base64.
    
    Returns:
        str: The encrypted token as a string.
        
    Raises:
        ValueError: If the token is empty or too short, or if the key is invalid.
        RuntimeError: If any other error occurs during encryption.
    """
    try:
        if not token or not token.strip():
            raise ValueError("Invalid token: Token cannot be empty or whitespace.")
        
        # Additional validation to ensure token is in expected format
        if len(token) < 8:  # Adjust based on Ponto API requirements
            raise ValueError("Token is too short. Ponto API requires minimum length of 8 characters.")
            
        # Validate the key
        try:
            Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {str(e)}")
            
        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(token.encode())  # Convert the token to bytes before encryption
        
        # Log with truncated token ID for traceability without exposing sensitive data
        token_prefix = token[:5] if len(token) > 5 else "****"
        logger.info(f"Token successfully encrypted (token prefix: {token_prefix}...).")
        
        return encrypted_token.decode()  # Return the encrypted token as a string
    
    except ValueError as ve:
        if "key" in str(ve).lower():
            logger.error(f"Invalid key provided for encryption: {str(ve)}")
            raise ValueError("The encryption key provided is invalid.") from ve
        else:
            logger.error(f"Invalid token format for encryption: {str(ve)}")
            raise ValueError("The token format is invalid for encryption.") from ve
    
    except Exception as e:
        logger.error(f"Error while encrypting token: {str(e)}", exc_info=True)
        # Use a more specific exception type 
        raise RuntimeError(f"Error while encrypting token: {str(e)}") from e


# Decryption function
def decrypt_token(encrypted_token: str, key: bytes) -> str:
    """Decrypt an encrypted token using Fernet symmetric encryption.
    
    Args:
        encrypted_token (str): The encrypted token to decrypt. Must not be empty.
        key (bytes): The Fernet key used for decryption. Must be the same key used for encryption.
    
    Returns:
        str: The decrypted token as a string.
        
    Raises:
        ValueError: If the encrypted token is empty or if the key is invalid.
        InvalidToken: If the encrypted token cannot be decrypted with the provided key.
        RuntimeError: If any other error occurs during decryption.
    """
    try:
        if not encrypted_token or not encrypted_token.strip():
            raise ValueError("Invalid token: Token cannot be empty or whitespace.")
            
        # Validate the key
        try:
            Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid decryption key format: {str(e)}")
            
        fernet = Fernet(key)
        decrypted_token = fernet.decrypt(encrypted_token.encode())  # Convert the encrypted token back to bytes
        
        # Log with truncated token data for traceability without exposing sensitive data
        token_preview = decrypted_token.decode()[:5] if len(decrypted_token) > 5 else "****"
        logger.info(f"Token successfully decrypted (token prefix: {token_preview}...).")
        
        return decrypted_token.decode()
    
    except InvalidToken as it:
        token_preview = encrypted_token[:5] if len(encrypted_token) > 5 else "****"
        logger.error(f"Invalid token provided for decryption (token prefix: {token_preview}...): {str(it)}")
        raise InvalidToken("The encrypted token is invalid.") from it
    
    except ValueError as ve:
        logger.error(f"Invalid key or token provided for decryption: {str(ve)}")
        raise ValueError("The decryption key provided is invalid.") from ve
    
    except Exception as e:
        logger.error(f"Error while decrypting token: {str(e)}", exc_info=True)
        raise RuntimeError(f"Error while decrypting token: {str(e)}") from e