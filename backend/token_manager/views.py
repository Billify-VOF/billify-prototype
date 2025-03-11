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
from utils.base import encrypt_token,decrypt_token
import logging
from dotenv import load_dotenv
load_dotenv()

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



if key is None:
    logger.error("FERNET_KEY not found in the .env file!")
    raise ValueError("FERNET_KEY not found in the .env file!")
# Ensure the key is valid (it should be a byte string)
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
        context.check_hostname = False
        
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
        if response.status == 200:
            try:
                token_data = response.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in")
                user_id = 1
                user = User.objects.get(id=user_id)
                # Encrypt the tokens before saving to the database
                encrypted_access_token = encrypt_token(access_token,key)
                encrypted_refresh_token = encrypt_token(refresh_token,key)
                try:
                    ponto_token = PontoToken.objects.get(user=user)
                    ponto_token.access_token = encrypted_access_token
                    ponto_token.refresh_token = encrypted_refresh_token
                    ponto_token.expires_in = expires_in
                    ponto_token.save()
                except PontoToken.DoesNotExist:
                    PontoToken.objects.create(
                        user=user,
                        access_token=encrypted_access_token,
                        refresh_token=encrypted_refresh_token,
                        expires_in=expires_in
                    )
                return Response({
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": token_data.get("expires_in"),
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


# get access token 
def refresh_access_token():
    """
    Refreshes the access token using the stored refresh token, updates it in the database,
    and returns the updated token.
    """
    user_id = 1 
    try:
        # Retrieve the user's PontoToken instance
        ponto_token = PontoToken.objects.get(user=user_id)
        if not ponto_token.refresh_token:
            return {"error": "Refresh token not found"}
        # Decrypt the stored refresh token
        decrypted_refresh_token = decrypt_token(ponto_token.refresh_token,key)
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
        context.check_hostname = False

        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_REQUIRED,
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
        if response.status == 200:
            token_data = json.loads(response.data.decode('utf-8'))
            encrypted_access_token = encrypt_token(token_data.get("access_token"),key)
            encrypted_refresh_token = encrypt_token(token_data.get("refresh_token", decrypted_refresh_token),key)
            # Update the stored access token and refresh token in the database
            ponto_token.access_token = encrypted_access_token
            ponto_token.refresh_token = encrypted_refresh_token
            ponto_token.expires_in = token_data.get("expires_in")
            ponto_token.save()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
            }

        else:
            logger.error(f"User {user_id} - Failed to refresh access token: {response.data.decode('utf-8')}")
            return {"error": "Failed to refresh access token"}

    except Exception as e:
        return {"error": "No tokens found for this user"}
    except Exception as e:
        logger.error(f"User {user_id} - Error occurred: {str(e)}")
        return {"error": str(e)}

    

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
    access_token = decrypt_token(get_token.access_token,key)
    return access_token

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
def fetch_account_details(request):
    """Fetches accounts from the Ponto Connect API."""
    user_id = 1
    token = get_access_token(user_id)
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

    # Make the GET request using the PoolManager
    try:
        response = http.request(
            'GET',
            API_BASE_URL,
            headers=headers
        )
        accounts_data = json.loads(response.data.decode('utf-8'))
        user = User.objects.get(id=user_id)
        save_record =save_or_update_account(user,accounts_data)
        return Response(save_record)

    except Exception as e:
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
                'availableBalance': account_data['data'][0]['attributes']['availableBalance'],
                'subtype': account_data['data'][0]['attributes']['subtype'],
                'holder_name': account_data['data'][0]['attributes']['holderName'],
                'resourceId': account_data['data'][0]['meta']['latestSynchronization']['attributes']['resourceId']
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
            account.availableBalance = account_data['data'][0]['attributes']['availableBalance']
            account.subtype = account_data['data'][0]['attributes']['subtype']
            account.holder_name = account_data['data'][0]['attributes']['holderName']
            account.resourceId= account_data['data'][0]['meta']['latestSynchronization']['attributes']['resourceId']
            account.save()
        
        # Serialize the saved or updated object
        serializer = IbanityAccountSerializer(account)
        return serializer.data
    
    except Exception as e:
        return {"error": f"Failed to save or update account: {e}"}
    
    except Exception as e:
        return None

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
        return Response(accounts_data)
    except Exception as e:
        return Response({"error": f"Request failed: {e}"}, status=500)


@api_view(['POST'])
def Create_Payment(request):
    try:
        # Get the JSON payload from the request
        payload = json.loads(request.body)
        
        # Get account ID from database or request
        user_id = 1
        get_resourceId = IbanityAccount.objects.filter(id=user_id).first()
        if not get_resourceId:
            return Response({"error": "Account not found for the given user ID"}, status=404)
        
        # account_id = get_resourceId.account_id
        account_id = '1ab6024c-fc81-4a69-ad65-e4155589631e'
        account_type = get_resourceId.product
        if not account_id:
            
        # if account_type != "Current account" or account_type != "Checking account":
            return Response({"error": "Account ID provide"}, status=400)
        # Construct the API URL
        API_BASE_URL = f"https://api.ibanity.com/ponto-connect/accounts/{account_id}/payments"
        created = str(int(time.time()))

        # Calculate the digest
        data = "" # No data for GET request
        digest_hash = hashlib.sha512(data.encode('utf-8')).digest()
        digest = "SHA-512=" + base64.b64encode(digest_hash).decode('utf-8')
        request_target = "get /ponto-connect/accounts"
        # Get access token
        token = get_access_token(user_id)
        get_certificate_credentials = get_ibanity_credentials()
        signature = create_signature(request_target, digest, created, get_certificate_credentials['private_key_path'], get_certificate_credentials['private_key_password'])

        # Construct the Signature header
        signature_header = f"""keyId="{get_certificate_credentials['KEY_ID']}",created={created},algorithm="rsa-sha256",headers="(request-target) digest (created) host",signature="{signature}" """

        headers = {"Authorization": f"Bearer {token}"}
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=get_certificate_credentials['certificate_path'], keyfile=get_certificate_credentials['private_key_path'], password=get_certificate_credentials['private_key_password'])
        context.check_hostname = False
        # Get certificate credentials
        
        # Create headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        http = urllib3.PoolManager(
            num_pools=50,
            cert_reqs=ssl.CERT_NONE,  
            ca_certs=None,
            ssl_context=context
        )
        # Make POST request with certificate file
        response = http.request(
            'POST',
            API_BASE_URL,
            headers=headers,
        )
        if response.status == 201:  # Success
            create_payment_response = response.json()
            return Response(create_payment_response, status=201)
        elif response.status == 400:  # Bad Request
            error_response = response.json()
            if "paymentsCheckingAccountOnly" in [error['code'] for error in error_response['errors']]:
                return Response({"error": "Only checking accounts are supported for payment creation"}, status=400)
            else:
                return Response(error_response, status=response.status)
        else:  # Error response from API
            error_response = response.json()
            return Response(error_response, status=response.status)
    
    except json.JSONDecodeError:
        return Response({"error": f"Invalid JSON payload: {e}"}, status=400)
    except Exception as e:
        return Response({"error": f"Request failed: {e}"}, status=500)


