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

# Example usage
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
