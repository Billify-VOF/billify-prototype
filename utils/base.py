from cryptography.fernet import Fernet, InvalidToken
import os
import logging
from dotenv import load_dotenv

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()


key = os.getenv('FERNET_KEY')
if key is None:
    raise ValueError("FERNET_KEY not found in the .env file!")

# Ensure the key is valid (it should be a byte string)
key = key.encode()

def generate_key() -> bytes:
    """Generate a new Fernet key for encryption/decryption.
    
    Returns:
        bytes: A new Fernet key that can be stored in the .env file.
    """
    return Fernet.generate_key()

# Encryption function
def encrypt_token(token: str, key: bytes) -> str:
   
    try:
        if not token or not token.strip():
            raise ValueError("Invalid token: Token cannot be empty or whitespace.")
        
        # Additional validation to ensure token is in expected format
        if len(token) < 8:  # Example validation - adjust based on your actual requirements
            raise ValueError("Token is too short. Expected minimum length: 8")
            
        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(token.encode())  # Convert the token to bytes before encryption
        
        # Log with truncated token ID for traceability without exposing sensitive data
        token_prefix = token[:5] if len(token) > 5 else "****"
        logger.info(f"Token successfully encrypted (token prefix: {token_prefix}...).")
        
        return encrypted_token.decode()  # Return the encrypted token as a string
    
    except ValueError as ve:
        logger.error(f"Invalid key provided for encryption: {str(ve)}")
        raise ValueError("The encryption key provided is invalid.") from ve
    
    except Exception as e:
        logger.error(f"Error while encrypting token: {str(e)}")
        raise Exception(f"Error while encrypting token: {str(e)}") from e


# Decryption function
def decrypt_token(encrypted_token: str, key: bytes) -> str:
    
    try:
        if not encrypted_token or not encrypted_token.strip():
            raise ValueError("Invalid token: Token cannot be empty or whitespace.")
            
        fernet = Fernet(key)
        decrypted_token = fernet.decrypt(encrypted_token.encode())  # Convert the encrypted token back to bytes
        
        # Log with truncated token data for traceability without exposing sensitive data
        token_preview = decrypted_token.decode()[:5] if len(decrypted_token) > 5 else "****"
        logger.info(f"Token successfully decrypted (token prefix: {token_preview}...).")
        
        return decrypted_token.decode()
    
    except InvalidToken as it:
        logger.error(f"Invalid token provided for decryption: {str(it)}")
        raise InvalidToken("The encrypted token is invalid.") from it
    
    except ValueError as ve:
        logger.error(f"Invalid key provided for decryption: {str(ve)}")
        raise ValueError("The decryption key provided is invalid.") from ve
    
    except Exception as e:
        logger.error(f"Error while decrypting token: {str(e)}")
        raise Exception(f"Error while decrypting token: {str(e)}") from e