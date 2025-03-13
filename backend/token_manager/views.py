import os
import json
import string
import base64
import ssl
import urllib3
import secrets
import logging
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dotenv import load_dotenv
from utils.base import encrypt_token, decrypt_token
from token_manager.models import PontoToken

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
key = os.getenv('FERNET_KEY')

if key is None:
    raise ValueError("FERNET_KEY not found in the .env file!")
key = key.encode()

def convertclientidsecret(client_id, client_secret):
    
    # Concatenate client_id and client_secret with a colon
    client_credentials = f"{client_id}:{client_secret}"
    # Base64 encode the client credentials
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')

    return encoded_credentials


def generate_random_session_id():
    random_number = ''.join(secrets.choice(string.digits) for _ in range(50))  # Generate a secure random 50-digit number
    return f"session_{random_number}"


@api_view(['GET'])
def ponto_login(request):
    """
    Handles both the redirection to Ponto's OAuth2 login page and the callback to exchange the authorization code for an access token.
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
    AUTHCODE = request.GET.get('code')
    if not AUTHCODE:
        # Redirect user to Ponto's login page if no code is provided
        return redirect(auth_url)

    # Step 2: Exchange authorization code for access token
    try:
        url = URL
        PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')
        if not AUTHCODE:
                return Response({"error": "No authorization code received"}, status=400)
        client = convertclientidsecret(PONTO_CLIENT_ID, PONTO_CLIENT_SECRET)
        
        # Prepare request data for the token exchange
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Basic {client}"
        }
        
        data = {
            "grant_type": "authorization_code", 
            "code": AUTHCODE,                  
            "redirect_uri": PONTO_REDIRECT_URI,
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
            ca_certs=urllib3.util.ssl_.DEFAULT_CABUNDLE_PATH,
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
                token_data = json.loads(response.data.decode('utf-8'))
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in")
                user_id = request.user
                user = User.objects.get(id=user_id)
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
                logging.exception("Failed to decode JSON response from Ponto server")
                return Response({"error": "Invalid JSON response from server"}, status=500)
        else:
            logging.error(f"Failed to get access token: {response.status}, {response.data.decode('utf-8')}")
            return Response({
                "error": "Failed to get access token",
                "details": response.data.decode('utf-8')
            }, status=500)

    except Exception as e:
        logging.exception(f"Unexpected error in ponto_login: {str(e)}")
        return Response({'message': str(e)})
    

# get access token 
def refresh_access_token(request):
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
            ca_certs=urllib3.util.ssl_.DEFAULT_CABUNDLE_PATH,
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
            token_data = json.loads(response.data.decode('utf-8'))
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
            return Response({"error": "Failed to refresh access token"}, status=response.status)

    except PontoToken.DoesNotExist:
        logger.error(f"User {user} - No PontoToken found")
        return Response({"error": "No token found for this user"}, status=404)
        
    except Exception as e:
        logger.error(f"User {user} - Error occurred: {str(e)}")
        return Response({"error": str(e)}, status=500)