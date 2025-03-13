from django.shortcuts import render
import os
import json
import requests
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect
from requests.auth import HTTPBasicAuth
import random
import string
import base64
import ssl
from OpenSSL import crypto
from urllib.parse import urlencode
import urllib3
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding
import time
from token_manager.models import IbanityAccount
from .serializers import IbanityAccountSerializer
import secrets
from .models import *
import logging
from utils.base import encrypt_token,decrypt_token
import certifi


from dotenv import load_dotenv
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

logger = logging.getLogger(__name__)

if key is None:
    raise ValueError("FERNET_KEY not found in the .env file!")
key = key.encode()

AUTHCODE =''

def convertclientidsecret(client_id, client_secret):
    
    # Concatenate client_id and client_secret with a colon
    client_credentials = f"{client_id}:{client_secret}"
    # Base64 encode the client credentials
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')

    return encoded_credentials


def generate_random_session_id():
    random_number = ''.join(random.choices(string.digits, k=50))  # Generate a random 50-digit number
    return f"session_{random_number}"

    

def load_private_key(private_key_path, password):
    # Read and load the private key
    with open(private_key_path, 'rb') as key_file:
        private_key_data = key_file.read()

    # Decrypt the private key with the provided password
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, passphrase=password.encode())
    return private_key


#Get Access token from Ponto token model
def get_access_token(user):
    try:
        get_token = PontoToken.objects.get(user=user)
        access_token = decrypt_token(get_token.access_token,key)
        return access_token
    except Exception as e:
        logger.error(f"Error while retrieving the access token for user {user.id}: {e}")
        return None


API_BASE_URL = f"{BASE_URL}accounts?page[limit]=3"

certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
private_key_password = PRIVATE_KEY_PASSWORD
KEY_ID = KEY_ID # Replace with your actual Key ID

def get_ibanity_credentials():
    """
    Returns the credentials and API base URL for the Ibanity API.

    Returns:
    - A dictionary containing the API base URL, certificate path, private key path, private key password, and key ID.
    """
    # API_BASE_URL = f"{BASE_URL}accounts?page[limit]=3"
    certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
    private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
    private_key_password = PRIVATE_KEY_PASSWORD
    KEY_ID = os.getenv('KEY_ID')  # Replace with your actual Key ID

    return {
        "API_BASE_URL": API_BASE_URL,
        "certificate_path": certificate_path,
        "private_key_path": private_key_path,
        "private_key_password": private_key_password,
        "KEY_ID": KEY_ID
    }


#Fetch Account balance retrieval
@api_view(['GET'])
def fetch_account_details(request):
    """Fetches accounts from the Ponto Connect API."""
    user = request.user
    token = get_access_token(user)
    created = str(int(time.time()))

    # Calculate the digest
    data = ""
    digest_hash = hashlib.sha512(data.encode('utf-8')).digest()
    digest = "SHA-512=" + base64.b64encode(digest_hash).decode('utf-8')

    # Create the signature
    request_target = "get /ponto-connect/accounts"

    headers = {"Authorization": f"Bearer {token}"}
    # Create an SSL context with the private key password
    context = ssl.create_default_context()
    context.load_cert_chain(certfile=certificate_path, keyfile=private_key_path, password=PRIVATE_KEY_PASSWORD)
    context.check_hostname = False

    # Create a PoolManager with the SSL context
    http = urllib3.PoolManager(
        num_pools=50,
        cert_reqs=ssl.CERT_NONE,  
        ca_certs=None,
        ssl_context=context
    )

    try:
        response = http.request(
            'GET',
            API_BASE_URL,
            headers=headers
        )
        accounts_data = json.loads(response.data.decode('utf-8'))
        user = User.objects.get(id=user)
        save_record =save_or_update_account(user,accounts_data)
        return Response(save_record)

    except Exception as e:
        logger.error(f"Error occurred while fetching account details for user {user}: {str(e)}")
        return Response({"error": f"Request failed: {e}"}, status=500)


#Save and update the record in db
def save_or_update_account(user, account_data):
    try:
        # Check if account already exists for the user
        account, created = IbanityAccount.objects.get_or_create(
            user=user,
            account_id=account_data['data'][0]['id'],
            defaults={
                'description': account_data['data'][0]['attributes']['description'],
                'product': account_data['data'][0]['attributes']['product'],
                'reference': account_data['data'][0]['attributes']['reference'],
                'currency': account_data['data'][0]['attributes']['currency'],
                'authorization_expiration_expected_at': account_data['data'][0]['attributes']['authorizationExpirationExpectedAt'],
                'current_balance': account_data['data'][0]['attributes']['currentBalance'],
                'available_balance': account_data['data'][0]['attributes']['availableBalance'],
                'subtype': account_data['data'][0]['attributes']['subtype'],
                'holder_name': account_data['data'][0]['attributes']['holderName'],
                'resource_id': account_data['data'][0]['meta']['latestSynchronization']['attributes']['resourceId']
            }
        )
        
        if not created:
            # Update existing account
            account.description = account_data['data'][0]['attributes']['description']
            account.product = account_data['data'][0]['attributes']['product']
            account.reference = account_data['data'][0]['attributes']['reference']
            account.currency = account_data['data'][0]['attributes']['currency']
            account.authorization_expiration_expected_at = account_data['data'][0]['attributes']['authorizationExpirationExpectedAt']
            account.current_balance = account_data['data'][0]['attributes']['currentBalance']
            account.available_balance = account_data['data'][0]['attributes']['availableBalance']
            account.subtype = account_data['data'][0]['attributes']['subtype']
            account.holder_name = account_data['data'][0]['attributes']['holderName']
            account.resource_id= account_data['data'][0]['meta']['latestSynchronization']['attributes']['resourceId']
            account.save()
        
        # Serialize the saved or updated object
        serializer = IbanityAccountSerializer(account)
        return serializer.data
    
    except Exception as e:
        logger.error(f"Failed to save or update account for user: {user.id}, error: {e}")
        return {"error": f"Failed to save or update account: {e}"}
    
    except Exception as e:
        return None



