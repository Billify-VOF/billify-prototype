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
import logging



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
                
                try:
                    ponto_token = PontoToken.objects.get(user=user)
                    ponto_token.access_token = access_token
                    ponto_token.refresh_token = refresh_token
                    ponto_token.expires_in = expires_in
                    ponto_token.save()
                except PontoToken.DoesNotExist:
                    PontoToken.objects.create(
                        user=user,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expires_in=expires_in
                    )
                return Response({
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": token_data.get("expires_in"),
                })
            except JSONDecodeError:
                # Handle invalid JSON response from the server
                logging.exception("Failed to decode JSON response from Ponto server")
                return Response({"error": "Invalid JSON response from server"}, status=500)
        else:
            logging.error(f"Failed to get access token: {response.status}, {response.text}")
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
    user_id = 1  # Example user_id, adjust as needed
    try:
        # Retrieve the user's PontoToken instance
        ponto_token = PontoToken.objects.get(user=user_id)

        if not ponto_token.refresh_token:
            return {"error": "Refresh token not found"}

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
            "refresh_token": ponto_token.refresh_token,
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

            # Update the stored access token and refresh token in the database
            ponto_token.access_token = token_data.get("access_token")
            ponto_token.refresh_token = token_data.get("refresh_token", ponto_token.refresh_token)
            ponto_token.expires_in = token_data.get("expires_in")
            ponto_token.save()

            # Return the updated access token data
            return {
                "access_token": ponto_token.access_token,
                "refresh_token": ponto_token.refresh_token,
                "expires_in": ponto_token.expires_in,
            }

        else:
            logging.error(f"Failed to refresh access token: {response.status}, {response.data.decode('utf-8')}")
            return {"error": "Failed to refresh access token"}

    except PontoToken.DoesNotExist:
        logging.exception("No PontoToken found for this user")
        return {"error": "No tokens found for this user"}
    except Exception as e:
        logging.exception("Network error occurred while refreshing the access token")
        return {"error": str(e)}