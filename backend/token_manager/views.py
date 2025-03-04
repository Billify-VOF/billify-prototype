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
    Handles both the redirection to Ponto's OAuth2 login page and the callback to exchange the authorization code for an access token.
    """
    
    session_id = generate_random_session_id()
    auth_url = f"{os.getenv('PONTO_AUTH_URL')}?client_id={os.getenv('PONTO_CLIENT_ID')}&redirect_uri={os.getenv('PONTO_REDIRECT_URI')}&response_type=code&scope=ai pi&state={session_id}"
    
    # Get 'code' from query parameters (callback step)
    AUTHCODE = request.GET.get('code')
    if not AUTHCODE:
        # Redirect user to Ponto's login page if no code is provided
        return redirect(auth_url)

    # Step 2: Exchange authorization code for access token
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
            # "code": code,                  
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


def load_private_key(private_key_path, password):
    # Read and load the private key
    with open(private_key_path, 'rb') as key_file:
        private_key_data = key_file.read()

    # Decrypt the private key with the provided password
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, passphrase=password.encode())
    return private_key


#Get Access token from Tokens folder
def get_access_token():
    # Load access token from file
    token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tokens', 'tokens.json')
    with open(token_path, 'r') as f:
        token_info = json.load(f)
        
        return token_info['access_token']


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
    token = get_access_token()
    user_id = 1
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
        print(f"Failed to save or update account: {e}")
        return {"error": f"Failed to save or update account: {e}"}
    
    except Exception as e:
        print(f"Failed to save or update account: {e}")
        return None


#Get transaction History
@api_view(['GET'])
def get_transaction_history(request):

    user_id = 1
    token = get_access_token()
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
        return Response({'ok'})
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
        
        account_id = get_resourceId.account_id
        account_type = get_resourceId.product
        if account_type != "Current account" or account_type != "Checking account":
            return Response({"error": "Only checking accounts are supported for payment creation"}, status=400)
        # Construct the API URL
        API_BASE_URL = f"https://api.ibanity.com/ponto-connect/accounts/{account_id}/payments"
        created = str(int(time.time()))

        # Calculate the digest
        data = "" # No data for GET request
        digest_hash = hashlib.sha512(data.encode('utf-8')).digest()
        digest = "SHA-512=" + base64.b64encode(digest_hash).decode('utf-8')
        request_target = "get /ponto-connect/accounts"
        # Get access token
        token = get_access_token()
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


