"""Token management views for Ponto integration."""
import os
import json
import string
import base64
import ssl
import urllib3
from urllib3.util.ssl_ import DEFAULT_CABUNDLE_PATH
import secrets
import logging
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dotenv import load_dotenv
from token_manager.utils.base import encrypt_token, decrypt_token, get_encryption_key
from token_manager.models import PontoToken, IbanityAccount
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from OpenSSL import crypto
from typing import Union, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

required_env_vars = [
    'PONTO_CLIENT_ID', 'PONTO_CLIENT_SECRET', 'PONTO_AUTH_URL', 
    'PONTO_TOKEN_URL', 'PONTO_REDIRECT_URI', 'URL', 
    'PRIVATE_KEY_PASSWORD', 'KEY_ID', 'BASE_URL'
]

# Check if any of the required environment variables are missing
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

# If there are any missing variables, raise an error with the list of missing vars
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

PONTO_CLIENT_ID = os.getenv('PONTO_CLIENT_ID')
PONTO_CLIENT_SECRET = os.getenv('PONTO_CLIENT_SECRET')
PONTO_AUTH_URL = os.getenv('PONTO_AUTH_URL')
PONTO_TOKEN_URL = os.getenv('PONTO_TOKEN_URL')
PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')
URL = os.getenv('URL')
PRIVATE_KEY_PASSWORD = os.getenv('PRIVATE_KEY_PASSWORD')
KEY_ID = os.getenv('KEY_ID')
BASE_URL = os.getenv('BASE_URL')

# Get the encryption key
key = get_encryption_key()

def convertclientidsecret(client_id: str, client_secret: str) -> str:
    """Convert client ID and secret to a Base64-encoded string.
    
    Args:
        client_id (str): The client ID.
        client_secret (str): The client secret.
        
    Returns:
        str: Base64-encoded client credentials.
    """
    # Concatenate client_id and client_secret with a colon
    client_credentials = f"{client_id}:{client_secret}"
    # Base64 encode the client credentials
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')

    return encoded_credentials


def generate_random_session_id() -> str:
    """Generate a random session ID.
    
    Returns:
        str: A randomly generated session ID.
    """
    random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50))  # Generate a secure random 50-character alphanumeric string
    return f"session_{random_string}"


def load_private_key(private_key_path: str, password: str):
    """Load and decrypt a private key from a file.
    
    Args:
        private_key_path (str): Path to the private key file.
        password (str): Password to decrypt the private key.
        
    Returns:
        object: The loaded private key.
    """
    # Read and load the private key
    with open(private_key_path, 'rb') as key_file:
        private_key_data = key_file.read()

    # Decrypt the private key with the provided password
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, passphrase=password.encode())
    return private_key


@api_view(['GET'])
def ponto_login(request: HttpRequest) -> Response:
    """
    Handles both the redirection to Ponto's OAuth2 login page and the callback to exchange the authorization code for an access token.
    
    Args:
        request: The HTTP request.
        
    Returns:
        Response: The redirect or token response.
    """
    
    session_id = generate_random_session_id()
    auth_url = (
        f"{os.getenv('PONTO_AUTH_URL')}?"
        f"client_id={os.getenv('PONTO_CLIENT_ID')}&"
        f"redirect_uri={os.getenv('PONTO_REDIRECT_URI')}&"
        f"response_type=code&"
        f"scope=ai+pi+offline_access&"
        f"state={session_id}"
    )
    auth_code = request.GET.get('code')
    if not auth_code:
        # Redirect user to Ponto's login page if no code is provided
        return redirect(auth_url)

    # Step 2: Exchange authorization code for access token
    try:
        url = URL
        ponto_redirect_uri = os.getenv('PONTO_REDIRECT_URI')
        client = convertclientidsecret(PONTO_CLIENT_ID, PONTO_CLIENT_SECRET)
        
        # Prepare request data for the token exchange
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Basic {client}"
        }
        
        data = {
            "grant_type": "authorization_code", 
            "code": auth_code,                  
            "redirect_uri": ponto_redirect_uri,
        }
        
        encoded_data = urlencode(data).encode('utf-8')
        # Create a PoolManager with the SSL context
        certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
        private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
        private_key_password = PRIVATE_KEY_PASSWORD  # Password for the encrypted private key
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=certificate_path, keyfile=private_key_path, password=private_key_password)
        context.check_hostname = True
        
        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_REQUIRED, 
            ca_certs=DEFAULT_CABUNDLE_PATH,
            ssl_context=context
        )
        
        response = http.request(
            'POST',
            url,
            headers=headers,
            body=encoded_data,
            preload_content=True
        )
        
        # Process the response
        if response.status == 200:
            try:
                token_data: Dict[str, Any] = json.loads(response.data.decode('utf-8'))
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in")
                user = request.user
                # Encrypt the tokens before saving to the database
                encrypted_access_token = encrypt_token(access_token, key)
                encrypted_refresh_token = encrypt_token(refresh_token, key)
                ponto_token, created = PontoToken.objects.get_or_create(
                    user=user,
                    defaults={
                        'access_token': encrypted_access_token,
                        'refresh_token': encrypted_refresh_token,
                        'expires_in': expires_in,
                    }
                )
                
                if not created:  # If the token already exists, update it
                    ponto_token.access_token = encrypted_access_token
                    ponto_token.refresh_token = encrypted_refresh_token
                    ponto_token.expires_in = expires_in
                    ponto_token.save()
                return Response({
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": token_data.get("expires_in"),
                })
            except json.JSONDecodeError:
                logger.exception("Failed to decode JSON response from Ponto server")
                return Response({"error": "Invalid JSON response from server"}, status=500)
        else:
            logger.error(f"Failed to get access token: {response.status}, {response.data.decode('utf-8')}")
            return Response({
                "error": "Failed to get access token",
                "details": response.data.decode('utf-8')
            }, status=500)

    except Exception as e:
        logger.exception(f"Unexpected error in ponto_login: {str(e)}")
        return Response({'message': str(e)})

# Get access token from Ponto token model
def get_access_token(user) -> Union[str, Response]:
    """Get the access token for a user.
    
    Args:
        user: The user to get the access token for.
        
    Returns:
        Union[str, Response]: The decrypted access token or error response.
    """
    try:
        get_token = PontoToken.objects.get(user=user)
        access_token = decrypt_token(get_token.access_token, key)
        return access_token
    except Exception as e:
        logger.error(f"Access token not found for user {user}")
        return Response({f"Error while retrieving the access token:{str(e)}"})


API_BASE_URL = f"{BASE_URL}accounts?page[limit]=3"

certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
private_key_password = PRIVATE_KEY_PASSWORD

def get_ibanity_credentials() -> dict:
    """
    Returns the credentials and API base URL for the Ibanity API.

    Returns:
        dict: A dictionary containing the API base URL, certificate path, private key path, private key password, and key ID.
    """
    cert_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
    priv_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
    priv_key_pass = PRIVATE_KEY_PASSWORD
    key_id = os.getenv('KEY_ID')  # Replace with your actual Key ID

    return {
        "API_BASE_URL": API_BASE_URL,
        "certificate_path": cert_path,
        "private_key_path": priv_key_path,
        "private_key_password": priv_key_pass,
        "KEY_ID": key_id
    }


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
    """
    signing_string = f"""(request-target): {request_target}\ndigest: {digest}\n(created): {created}\nhost: api.ibanity.com"""
    
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


def refresh_access_token(request: HttpRequest):
    """
    Refreshes the access token using the stored refresh token, updates it in the database,
    and returns the updated token.
    """
    user = request.user
    # Ensure user is authenticated
    if not user.is_authenticated:
        return Response({"error": "User not authenticated"}, status=401)
        
    try:
        # Retrieve the user's PontoToken instance
        ponto_token = PontoToken.objects.get(user=user)
        if not ponto_token.refresh_token:
            return Response({"error": "Refresh token not found"}, status=400)
        # Decrypt the stored refresh token
        decrypted_refresh_token = decrypt_token(ponto_token.refresh_token, key)
        # Prepare request data for refreshing the token
        url = os.getenv('URL')
        client_id = os.getenv('PONTO_CLIENT_ID')
        client_secret = os.getenv('PONTO_CLIENT_SECRET')
        client = convertclientidsecret(client_id, client_secret)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Basic {client}"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": decrypted_refresh_token,
            "client_id": client_id,
        }
        encoded_data = urlencode(data).encode('utf-8')

        # Set up SSL context for cert and key
        certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
        private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
        private_key_password = os.getenv("PRIVATE_KEY_PASSWORD")  # Ensure you have this in your .env

        context = ssl.create_default_context()
        context.load_cert_chain(certfile=certificate_path, keyfile=private_key_path, password=private_key_password)
        context.check_hostname = True

        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs=DEFAULT_CABUNDLE_PATH,
            ssl_context=context
        )

        response = http.request(
            'POST',
            url,
            headers=headers,
            body=encoded_data,
            preload_content=True
        )
        if response.status == 200:
            token_data: Dict[str, Any] = json.loads(response.data.decode('utf-8'))
            encrypted_access_token = encrypt_token(token_data.get("access_token"), key)
            encrypted_refresh_token = encrypt_token(token_data.get("refresh_token", decrypted_refresh_token), key)
            # Update the stored access token and refresh token in the database
            ponto_token.access_token = encrypted_access_token
            ponto_token.refresh_token = encrypted_refresh_token
            ponto_token.expires_in = token_data.get("expires_in")
            ponto_token.save()

            return Response({
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
            }, status=200)

        else:
            logger.error(f"User {user} - Failed to refresh access token: {response.data.decode('utf-8')}")
            return Response({
                "error": "Failed to refresh access token",
                "details": response.data.decode('utf-8')
            }, status=response.status)

    except PontoToken.DoesNotExist:
        logger.error(f"User {user} - No PontoToken found")
        return Response({"error": "No token found for this user"}, status=404)
        
    except Exception as e:
        logger.error(f"User {user} - Error occurred: {str(e)}")

# Get transaction History
@api_view(['GET'])
def get_transaction_history(request: HttpRequest):
    """Get transaction history for a user's account.
    
    Args:
        request: The HTTP request.
        
    Returns:
        Response: The transaction history data.
    """
    try:
        user = request.user.id
        token = get_access_token(user)
        get_certificate_credentials = get_ibanity_credentials()
        get_resourceId = IbanityAccount.objects.filter(id=user).first()
        if not get_resourceId:
            return Response({"error": "No Ibanity account found for this user"}, status=404)
        account_id = get_resourceId.account_id
        api_url = f"{BASE_URL}accounts/{account_id}/transactions"

        # Create the request headers
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create an SSL context with the private key password
        context = ssl.create_default_context()
        context.load_cert_chain(
            certfile=get_certificate_credentials['certificate_path'], 
            keyfile=get_certificate_credentials['private_key_path'], 
            password=get_certificate_credentials['private_key_password']
        )
        context.check_hostname = False

        # Create a PoolManager with the SSL context
        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_NONE,  
            ca_certs=None,
            ssl_context=context
        )

        # Make the GET request using the PoolManager
        try:
            response = http.request(
                'GET',
                api_url,
                headers=headers
            )
            if response.status != 200:
                return Response(
                    {"error": f"API request failed with status {response.status}", "details": response.data.decode('utf-8')}, 
                    status=response.status
                )
            transactions_data: Dict[str, Any] = json.loads(response.data.decode('utf-8'))
            return Response(transactions_data)
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return Response({"error": f"Request failed: {e}"}, status=500)
    except PontoToken.DoesNotExist:
        return Response({"error": "No access token found for this user"}, status=401)
    except IbanityAccount.DoesNotExist:
        return Response({"error": "No Ibanity account found for this user"}, status=404)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": f"Request failed: {str(e)}"}, status=500)
