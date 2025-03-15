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

# Load the Fernet encryption key from environment variable
key = os.getenv('FERNET_KEY')
if key is None:
    logger.error("FERNET_KEY not found in the .env file!")
    raise ValueError("FERNET_KEY not found in the .env file!")

# Ensure the key is valid (it should be a byte string)
# Fernet keys must be 32 bytes base64-encoded (resulting in a 44-character string)
if len(key) != 44:
    logger.error("FERNET_KEY has invalid length. It should be a 44-character base64 encoded key.")
    raise ValueError("FERNET_KEY has invalid length. Please provide a valid 32-byte key encoded in base64.")
key = key.encode()

# Encryption function
def encrypt_token(token: str, key: bytes) -> str:
   
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
    
    try:
        if not encrypted_token or not encrypted_token.strip():
            raise ValueError("Invalid token: Token cannot be empty or whitespace.")
        fernet = Fernet(key)
        decrypted_token = fernet.decrypt(encrypted_token.encode())  # Convert the encrypted token back to bytes
        logger.debug("Token successfully decrypted.")
        return decrypted_token.decode()
    
    except InvalidToken as it:
        logger.error(f"Invalid token provided for decryption: {str(it)}")
        raise InvalidToken("The encrypted token is invalid or corrupted.") from it
    
    except ValueError as ve:
        logger.error(f"Invalid input provided for decryption: {str(ve)}")
        raise ValueError(f"Invalid input for decryption: {str(ve)}") from ve
    
    except Exception as e:
        logger.error(f"Error while decrypting token: {str(e)}")
        raise Exception(f"Error while decrypting token: {str(e)}") from e
