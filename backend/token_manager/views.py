from django.shortcuts import render
import os,json,requests
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



from dotenv import load_dotenv
load_dotenv()


PONTO_CLIENT_ID = os.getenv('PONTO_CLIENT_ID')
PONTO_CLIENT_SECRET = os.getenv('PONTO_CLIENT_SECRET')
PONTO_AUTH_URL = os.getenv('PONTO_AUTH_URL')
PONTO_TOKEN_URL = os.getenv('PONTO_TOKEN_URL')
PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')
URL = os.getenv('URL')
PRIVATE_KEY_PASSWORD = os.getenv('PRIVATE_KEY_PASSWORD')
KEY_ID = os.getenv('KEY_ID')
BASE_URL = os.getenv('BASE_URL')


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
    get_token = PontoToken.objects.get(user=user)
    return get_token.access_token


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


def create_signature(request_target, digest, created, private_key_path, private_key_password):
    """Creates the signature string."""
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

#Get transaction History
@api_view(['GET'])
def get_transaction_history(request):

    user_id = 1
    token = get_access_token(user_id)
    get_certificate_credentials =get_ibanity_credentials()
    get_resourceId = IbanityAccount.objects.filter(id=user_id).first()
    account_id = get_resourceId.account_id
    API_BASE_URL = f"{BASE_URL}accounts/{account_id}/transactions"
    created = str(int(time.time()))

    # Calculate the digest
    data = "" # No data for GET request
    digest_hash = hashlib.sha512(data.encode('utf-8')).digest()
    digest = "SHA-512=" + base64.b64encode(digest_hash).decode('utf-8')

    # Create the signature
    request_target = "get /ponto-connect/accounts"
    signature = create_signature(request_target, digest, created, get_certificate_credentials['private_key_path'], get_certificate_credentials['private_key_password'])

    # Construct the Signature header
    signature_header = f"""keyId="{get_certificate_credentials['KEY_ID']}",created={created},algorithm="rsa-sha256",headers="(request-target) digest (created) host",signature="{signature}" """

    headers = {"Authorization": f"Bearer {token}"}
    # Create an SSL context with the private key password
    context = ssl.create_default_context()
    context.load_cert_chain(certfile=get_certificate_credentials['certificate_path'], keyfile=get_certificate_credentials['private_key_path'], password=get_certificate_credentials['private_key_password'])
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
            API_BASE_URL,
            headers=headers
        )
        accounts_data = json.loads(response.data.decode('utf-8'))
        print(json.dumps(accounts_data),'accounts_data')
        return Response(accounts_data)
    except Exception as e:
        return Response({"error": f"Request failed: {e}"}, status=500)




