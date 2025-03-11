from cryptography.fernet import Fernet
import base64
import json
import os
from dotenv import load_dotenv
load_dotenv()


key = os.getenv('FERNET_KEY')
if key is None:
    raise ValueError("FERNET_KEY not found in the .env file!")

# Ensure the key is valid (it should be a byte string)
key = key.encode()

# def generate_key():
#     return Fernet.generate_key()
# Encryption function
def encrypt_token(token: str, key: bytes) -> str:
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(token.encode())  # Convert the token to bytes before encryption
    return encrypted_token.decode()  # Return the encrypted token as a string

# Decryption function
def decrypt_token(encrypted_token: str, key: bytes) -> str:
    fernet = Fernet(key)
    decrypted_token = fernet.decrypt(encrypted_token.encode())  # Convert the encrypted token back to bytes
    return decrypted_token.decode()