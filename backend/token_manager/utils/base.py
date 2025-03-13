from cryptography.fernet import Fernet, InvalidToken
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

# Generate a key (you should store this securely in your environment or configuration file)
def generate_key():
    return Fernet.generate_key()

# Get encryption key function
def get_encryption_key() -> bytes:
    """Get the encryption key from environment variables.
    
    Returns:
        bytes: The encryption key as bytes.
        
    Raises:
        ValueError: If the FERNET_KEY is not set in the environment.
    """
    key = os.getenv('FERNET_KEY')
    if key is None:
        logger.error("FERNET_KEY not found in the .env file!")
        raise ValueError("FERNET_KEY not found in the .env file!")
    
    # Ensure the key is valid (it should be a byte string)
    if isinstance(key, str):
        return key.encode()

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
    """
    try:
        if not token or not token.strip():
            raise ValueError("Invalid token: Token cannot be empty or whitespace.")
        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(token.encode())  # Convert the token to bytes before encryption
        logger.info("Token successfully encrypted.")
        return encrypted_token.decode()  # Return the encrypted token as a string
    
    except ValueError as ve:
        logger.error(f"Invalid key provided for encryption: {str(ve)}")
        raise ValueError("The encryption key provided is invalid.")
    
    except Exception as e:
        logger.error(f"Error while encrypting token: {str(e)}")
        raise Exception(f"Error while encrypting token: {str(e)}")

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
        raise InvalidToken("The encrypted token is invalid.")
    
    except ValueError as ve:
        logger.error(f"Invalid key provided for decryption: {str(ve)}")
        raise ValueError("The decryption key provided is invalid.")
    
    except Exception as e:
        logger.error(f"Error while decrypting token: {str(e)}")
        raise Exception(f"Error while decrypting token: {str(e)}")

# Example usage code - only runs when the file is executed directly
if __name__ == "__main__":
    # Example key generation (you should securely store this key)
    key = generate_key()
    # print(f"Generated Key: {key}")

    # Example tokens
    access_token = "zkk8qmiaBDrMuFLQzKtcCjNAjJ8D9-wbMWSRtwOsM-0.iCUmIPDFvXegvF_DFdohpWGJJ6O0HIP-3CYqRJ_D_H4"
    refresh_token = "dSE3_2IqmTkdHh_4ypIobWLKP06_nNMP0EAA9gHatgM.MmkJeV-ieuiQW8Oyyug-j2gbt3x5zbffjKeJpC744xI"

    # Encrypt the tokens
    encrypted_access_token = encrypt_token(access_token, key)
    encrypted_refresh_token = encrypt_token(refresh_token, key)

    print("\nEncrypted Access Token:", encrypted_access_token)
    print("Encrypted Refresh Token:", encrypted_refresh_token)

    # Decrypt the tokens
    decrypted_access_token = decrypt_token(encrypted_access_token, key)
    decrypted_refresh_token = decrypt_token(encrypted_refresh_token, key)

    print("\nDecrypted Access Token:", decrypted_access_token)
    print("Decrypted Refresh Token:", decrypted_refresh_token)
