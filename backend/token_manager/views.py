from django.shortcuts import render
import os,json,requests
import requests
import os
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


@api_view(['GET'])
def ponto_login(request):
    """
    Redirects the user to Ponto OAuth2 login page.
    """
    session_id = generate_random_session_id()
    auth_url = f"{PONTO_AUTH_URL}?client_id={PONTO_CLIENT_ID}&redirect_uri={PONTO_REDIRECT_URI}&response_type=code&scope=ai pi&state={session_id}"
    global AUTHCODE
    AUTHCODE = request.GET.get('code')
    return redirect(auth_url)



def load_private_key(private_key_path, password):
    # Read and load the private key
    with open(private_key_path, 'rb') as key_file:
        private_key_data = key_file.read()

    # Decrypt the private key with the provided password
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, passphrase=password.encode())
    return private_key


@api_view(['GET'])
def ponto_callback(request):
    """
    Handles Ponto callback and exchanges authorization code for access token.
    """
    try:

        url = URL
        PONTO_REDIRECT_URI = PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')
        if not AUTHCODE:
                return Response({"error": "No authorization code received"}, status=400)
        client = convertclientidsecret(PONTO_CLIENT_ID, PONTO_CLIENT_SECRET)
        # Prepare request data for the token exchange
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Basic {client}"
        }
        certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
        private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
        private_key_password = PRIVATE_KEY_PASSWORD  # Password for the encrypted private key
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=certificate_path, keyfile=private_key_path, password=private_key_password)
        context.check_hostname = False
        data = {
            "grant_type": "authorization_code", 
            "code": AUTHCODE,                  
            "redirect_uri": PONTO_REDIRECT_URI,
        }
        encoded_data = urlencode(data).encode('utf-8')
        # Create a PoolManager with the SSL context
        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_NONE, 
            ca_certs=None,
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
        if response.status== 200:
            try:
                token_data = json.loads(response.data.decode('utf-8'))
                token_data = response.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                token_info = {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
                token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tokens', 'tokens.json')
                with open(token_path, "w") as f:
                    json.dump(token_info, f, indent=4)
                return Response({
                    "access_token": access_token,
                    "refresh_token": refresh_token
                })
            except requests.exceptions.JSONDecodeError:
                return Response({"error": "Invalid JSON response from server"}, status=500)
        else:
            return Response({
                "error": "Failed to get access token",
                "details": response.text
            }, status=500)

    except Exception as e:
        return Response({'message': str(e)})


#Get Access token from Tokens folder
def get_access_token():
    # Load access token from file
    token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tokens', 'tokens.json')
    with open(token_path, 'r') as f:
        token_info = json.load(f)
        
        return token_info['access_token']


API_BASE_URL = f"{BASE_URL}'accounts'"
certificate_path = os.path.join(os.path.dirname(__file__), 'certificate.pem')
private_key_path = os.path.join(os.path.dirname(__file__), 'private_key.pem')
private_key_password = PRIVATE_KEY_PASSWORD
KEY_ID = KEY_ID # Replace with your actual Key ID

def create_signature(request_target, digest, created, private_key_path, private_key_password):
    """Creates the signature string."""
    signing_string = f"""(request-target): {request_target}\ndigest: {digest}\n(created): {created}\nhost: api.ibanity.com"""
    
    # Load the private key with the password
    with open(private_key_path, "rb") as key_file:
      private_key = serialization.load_pem_private_key(
          key_file.read(),
          password=private_key_password.encode(),  # Provide the password here
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

@api_view(['GET'])
def get_pass_key(request):
    """Fetches accounts from the Ponto Connect API."""
    token = get_access_token()
    # Get current timestamp as 'created' value
    created = str(int(time.time()))

    # Calculate the digest
    data = "" # No data for GET request
    digest_hash = hashlib.sha512(data.encode('utf-8')).digest()
    digest = "SHA-512=" + base64.b64encode(digest_hash).decode('utf-8')

    # Create the signature
    request_target = "get /ponto-connect/accounts"
    signature = create_signature(request_target, digest, created, private_key_path, PRIVATE_KEY_PASSWORD)

    # Construct the Signature header
    signature_header = f"""keyId="{KEY_ID}",created={created},algorithm="rsa-sha256",headers="(request-target) digest (created) host",signature="{signature}" """

    headers = {"Authorization": f"Basic {token}"}
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

    # Make the GET request using the PoolManager
    try:
        response = http.request(
            'GET',
            API_BASE_URL,
            headers=headers
        )
        accounts_data = json.loads(response.data.decode('utf-8'))
        return Response(accounts_data)

    except Exception as e:
        return Response({"error": f"Request failed: {e}"}, status=500)