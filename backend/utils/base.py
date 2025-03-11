from cryptography.fernet import Fernet
import base64
import json

# Generate a key (you should store this securely in your environment or configuration file)
def generate_key():
    return Fernet.generate_key()

# Encryption function
def encrypt_token(token: str, key: bytes) -> str:
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(token.encode())  # Convert the token to bytes before encryption
    return encrypted_token.decode()  # Return the encrypted token as a string

# Decryption function
def decrypt_token(encrypted_token: str, key: bytes) -> str:
    fernet = Fernet(key)
    decrypted_token = fernet.decrypt(encrypted_token.encode())  # Convert the encrypted token back to bytes
    return decrypted_token.decode()  # Return the decrypted token as a string


