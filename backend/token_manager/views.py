# Standard library imports
import base64
import json
import logging
import os
import ssl
import string

# Third-party imports
import certifi
import secrets
import urllib3
from OpenSSL import crypto
from dotenv import load_dotenv
from urllib.parse import urlencode

# Django imports
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Local imports
from .models import IbanityAccount, PontoToken
from .serializers import IbanityAccountSerializer
from .utils.base import encrypt_token, decrypt_token

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load environment variables
load_dotenv()

required_env_vars = [
    'PONTO_CLIENT_ID', 'PONTO_CLIENT_SECRET', 'PONTO_AUTH_URL', 
    'PONTO_TOKEN_URL', 'PONTO_REDIRECT_URI', 'URL', 
    'PRIVATE_KEY_PASSWORD', 'KEY_ID', 'BASE_URL', 'FERNET_KEY'
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
# Retrieve the FERNET_KEY (validation will be done in base.py)
key = os.getenv('FERNET_KEY').encode()

def convertclientidsecret(client_id, client_secret):
    """Concatenate and base64 encode client credentials."""
    client_credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')
    return encoded_credentials

def generate_random_session_id():
    """Generate a random session ID for authentication."""
    random_number = ''.join(secrets.choice(string.digits) for _ in range(50))
    return f"session_{random_number}"

def load_private_key(private_key_path, password):
    """Load and decrypt private key."""
    with open(private_key_path, 'rb') as key_file:
        private_key_data = key_file.read()
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, passphrase=password.encode())
    return private_key

def get_access_token(user):
    """Get decrypted access token for the specified user."""
    try:
        get_token = PontoToken.objects.get(user=user)
        access_token = decrypt_token(get_token.access_token, key)
        return access_token
    except PontoToken.DoesNotExist:
        logger.error(f"No token found for user {user.id}")
        return None
    except Exception as e:
        logger.error(f"Error while retrieving the access token for user {user.id}: {e}")
        return None

# API settings for account balance retrieval
API_BASE_URL = f"{BASE_URL}accounts?page[limit]=3"
certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
private_key_password = PRIVATE_KEY_PASSWORD

def get_ibanity_credentials(base_url=BASE_URL, key_id=KEY_ID, private_key_pwd=PRIVATE_KEY_PASSWORD):
    """Returns the credentials and API base URL for the Ibanity API."""
    return {
        "API_BASE_URL": f"{base_url}accounts?page[limit]=3",
        "certificate_path": certificate_path,
        "private_key_path": private_key_path,
        "private_key_password": private_key_pwd,
        "KEY_ID": key_id
    }

@api_view(['GET'])
def fetch_account_details(request):
    """Fetches accounts from the Ponto Connect API."""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
        
    user = request.user
    token = get_access_token(user)
    
    if not token:
        return Response({"error": "No access token found for user"}, status=404)

    # Create the signature
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an SSL context with the private key password
    context = ssl.create_default_context()
    context.load_cert_chain(certfile=certificate_path, keyfile=private_key_path, password=PRIVATE_KEY_PASSWORD)
    context.check_hostname = True

    # Create a PoolManager with the SSL context
    http = urllib3.PoolManager(
        num_pools=50,
        cert_reqs=ssl.CERT_REQUIRED,  
        ca_certs=certifi.where(),
        ssl_context=context
    )

    try:
        response = http.request(
            'GET',
            API_BASE_URL,
            headers=headers
        )
        accounts_data = json.loads(response.data.decode('utf-8'))
        
        # Check if the accounts data contains any accounts
        if not accounts_data.get('data'):
            return Response({"error": "No accounts found"}, status=404)
            
        save_record = save_or_update_account(user, accounts_data)
        
        if isinstance(save_record, dict) and "error" in save_record:
            return Response(save_record, status=500)
            
        return Response(save_record)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response for user {user}: {str(e)}")
        return Response({"error": f"Invalid JSON response: {e}"}, status=500)
    except urllib3.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching account details for user {user}: {str(e)}")
        return Response({"error": f"HTTP request failed: {e}"}, status=500)
    except Exception as e:
        logger.error(f"Error occurred while fetching account details for user {user}: {str(e)}")
        return Response({"error": f"Request failed: {e}"}, status=500)

def save_or_update_account(user, account_data):
    """Save or update account information in the database."""
    try:
        # Check if there are any accounts in the data
        if not account_data.get('data') or len(account_data['data']) == 0:
            return {"error": "No account data available"}
            
        # Validate account data structure
        account_info = account_data['data'][0]
        if 'id' not in account_info:
            return {"error": "Missing account ID in data"}
            
        if 'attributes' not in account_info:
            return {"error": "Missing attributes in account data"}
            
        attributes = account_info['attributes']
        required_attrs = ['description', 'product', 'reference', 'currency', 
                          'authorizationExpirationExpectedAt', 'currentBalance',
                          'availableBalance', 'subtype', 'holderName']
                          
        missing_attrs = [attr for attr in required_attrs if attr not in attributes]
        if missing_attrs:
            return {"error": f"Missing required attributes: {', '.join(missing_attrs)}"}
            
        # Validate meta data
        if ('meta' not in account_info or 
            'latestSynchronization' not in account_info['meta'] or
            'attributes' not in account_info['meta']['latestSynchronization'] or
            'resourceId' not in account_info['meta']['latestSynchronization']['attributes']):
            return {"error": "Missing resourceId in account data"}
            
        # Check if account already exists for the user
        account, created = IbanityAccount.objects.get_or_create(
            user=user,
            account_id=account_info['id'],
            defaults={
                'description': attributes['description'],
                'product': attributes['product'],
                'reference': attributes['reference'],
                'currency': attributes['currency'],
                'authorization_expiration_expected_at': attributes['authorizationExpirationExpectedAt'],
                'current_balance': attributes['currentBalance'],
                'available_balance': attributes['availableBalance'],
                'subtype': attributes['subtype'],
                'holder_name': attributes['holderName'],
                'resource_id': account_info['meta']['latestSynchronization']['attributes']['resourceId']
            }
        )
        
        if not created:
            # Map API fields to model fields
            field_mapping = {
                'description': 'description',
                'product': 'product',
                'reference': 'reference',
                'currency': 'currency',
                'authorizationExpirationExpectedAt': 'authorization_expiration_expected_at',
                'currentBalance': 'current_balance',
                'availableBalance': 'available_balance',
                'subtype': 'subtype',
                'holderName': 'holder_name'
            }
            
            # Update account fields
            for api_field, model_field in field_mapping.items():
                setattr(account, model_field, attributes[api_field])
                
            # Update resource_id separately since it's in a different structure
            account.resource_id = account_info['meta']['latestSynchronization']['attributes']['resourceId']
            account.save()
        
        # Serialize the saved or updated object
        serializer = IbanityAccountSerializer(account)
        return serializer.data
    
    except IndexError as e:
        logger.error(f"Invalid account data structure for user: {user.id}, error: {e}")
        return {"error": f"Invalid account data structure: {e}"}
    except KeyError as e:
        logger.error(f"Missing key in account data for user: {user.id}, error: {e}")
        return {"error": f"Missing data in account information: {e}"}
    except Exception as e:
        logger.error(f"Failed to save or update account for user: {user.id}, error: {e}")
        return {"error": f"Failed to save or update account: {e}"}

@api_view(['GET'])
def ponto_login(request):
    """
    Handles both the redirection to Ponto's OAuth2 login page and the callback
    to exchange the authorization code for an access token.
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
            ca_certs=certifi.where(),
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

@api_view(['POST'])
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
            ca_certs=certifi.where(),
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
            return Response({
                "error": "Failed to refresh access token",
                "details": response.data.decode('utf-8')
            }, status=response.status)

    except PontoToken.DoesNotExist:
        logger.error(f"User {user} - No PontoToken found")
        return Response({"error": "No token found for this user"}, status=404)
        
    except Exception as e:
        logger.error(f"User {user} - Error occurred: {str(e)}")
        return Response({"error": str(e)}, status=500)
