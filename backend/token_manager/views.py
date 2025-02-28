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

from dotenv import load_dotenv
load_dotenv()


# PONTO_CLIENT_ID = os.getenv('PONTO_CLIENT_ID')
# PONTO_CLIENT_SECRET = os.getenv('PONTO_CLIENT_SECRET')
# PONTO_AUTH_URL = os.getenv('PONTO_AUTH_URL')
# PONTO_TOKEN_URL = os.getenv('PONTO_TOKEN_URL')
# PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')
PONTO_CLIENT_ID = 'bb85a9ef-c106-4646-a53e-c8f405639208'
PONTO_CLIENT_SECRET = 'b89c0430-0823-47b0-a400-e7501e8ce4d4'
PONTO_AUTH_URL = "https://sandbox-authorization.myponto.com/oauth2/auth"
PONTO_TOKEN_URL = 'https://api.myponto.com/oauth2/token'
print(PONTO_TOKEN_URL,'PONTO_TOKEN_URL')
PONTO_REDIRECT_URI = "http://127.0.0.1:8003/api/ponto-login/"


def convertclientidsecret(client_id, client_secret):
    
    # Concatenate client_id and client_secret with a colon
    client_credentials = f"{client_id}:{client_secret}"
    # Base64 encode the client credentials
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')

    return encoded_credentials


def generate_random_session_id():
    random_number = ''.join(random.choices(string.digits, k=6))  # Generate a random 6-digit number
    return f"session_{random_number}"

@api_view(['GET'])
def ponto_login(request):
    """
    Redirects the user to Ponto OAuth2 login page.
    """
    session_id = generate_random_session_id()
    print(session_id,'ccccccc')
    # auth_url = (f"{PONTO_AUTH_URL}?client_id={PONTO_CLIENT_ID}"
    #             f"&redirect_uri={PONTO_REDIRECT_URI}&response_type=code&scope=ai pi&state={session_id}")
    # print('auth_url',auth_url)
    auth_url = f"{PONTO_AUTH_URL}?client_id={PONTO_CLIENT_ID}&redirect_uri={PONTO_REDIRECT_URI}&response_type=code&scope=ai pi&state=session_1234568"
    return redirect(auth_url)


import ssl
from OpenSSL import crypto

@api_view(['GET'])
def ponto_callback(request):
    """
    Handles Ponto callback and exchanges authorization code for access token.
    """
    try:
        url = "https://api.ibanity.com/ponto-connect/oauth2/token"
        PONTO_REDIRECT_URI = "http://127.0.0.1:8003/api/ponto-login/"
        # auth_code = request.GET.get('code')
        auth_code = 'Mc_2aWJc0G6OnlFib2m5zuGzOcoQwOTvQ_OR8CAEwDg.J9kNgQA_tNmo5FXr-mTzvDxdXPTyGCTufGZaHtLCGfk'

        if not auth_code:
            return Response({"error": "No authorization code received"}, status=400)

        # Prepare request data for the token exchange
        data = {
            "grant_type": "authorization_code",  # Correct grant_type for authorization code flow
            "code": auth_code,                   # The authorization code received
            "redirect_uri": PONTO_REDIRECT_URI,
        }

        # Convert client_id and client_secret to Base64 encoded string
        clientID = 'bb85a9ef-c106-4646-a53e-c8f405639208'
        clientSecret = 'b89c0430-0823-47b0-a400-e7501e8ce4d4'
        client = convertclientidsecret(clientID, clientSecret)

        # Prepare headers for the request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Basic {client}"
        }

        # Define file paths to your certificate and private key
        certificate_path = r"C:/Users/kunal/Downloads/application_bb85a9ef-c106-4646-a53e-c8f405639208/certificate.pem"
        private_key_path = r"C:/Users/kunal/Downloads/application_bb85a9ef-c106-4646-a53e-c8f405639208/private_key.pem"
        private_key_password = 'Billify-2'  # Password for the encrypted private key

        # # Load and decrypt the private key using the password
        private_key_data = open(private_key_path, 'rb').read()
        print('private_key_data',private_key_data)
        # private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data)
        # print('private_key',dir(private_key))
        # # if private_key.has_private():
        # private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_data, password=private_key_password.encode())
        # print('private_key===========',private_key)
        # # Prepare the SSLContext
        # context = ssl.create_default_context()
        # context.load_cert_chain(certfile=certificate_path, keyfile=private_key_path, password=private_key_password)

        # Send the request to the token URL
        response = requests.post(
            url,
            headers=headers,
            data=data,
            cert=(certificate_path, private_key_path,private_key_password),  # Provide certificate and private key
            verify=False  # Turn off verification for SSL (make sure to remove this for production)
        )

        print('response', response)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            try:
                token_data = response.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")

                return Response({
                    "access_token": access_token,
                    "refresh_token": refresh_token
                })
            except requests.exceptions.JSONDecodeError:
                return Response({"error": "Invalid JSON response from server"}, status=500)
        else:
            return Response({
                "error": "Failed to get access token",
                "details": response.text  # Log the raw response text instead of trying to parse it
            }, status=500)

    except Exception as e:
        return Response({'message': str(e)})


# Billify-2
# @api_view(['GET'])
# def ponto_callback(request):
#     """
#     Handles Ponto callback and exchanges authorization code for access token.
#     """ 
#     try:
#         # PONTO_TOKEN_URL = 'https://sandbox-authorization.myponto.com/oauth2/token'  # Updated URL
#         url = "https://api.ibanity.com/ponto-connect/oauth2/token"
#         PONTO_REDIRECT_URI = "http://127.0.0.1:8003/api/ponto-login/"
#         # auth_code =request.Get.get('code')
#         # Static authorization code for testing
#         auth_code = "Mc_2aWJc0G6OnlFib2m5zuGzOcoQwOTvQ_OR8CAEwDg.J9kNgQA_tNmo5FXr-mTzvDxdXPTyGCTufGZaHtLCGfk"
#         print(f"Using auth_code: {auth_code}")

#         if not auth_code:
#             auth_code = 'Mc_2aWJc0G6OnlFib2m5zuGzOcoQwOTvQ_OR8CAEwDg.J9kNgQA_tNmo5FXr-mTzvDxdXPTyGCTufGZaHtLCGfk'
#             return Response({"error": "No authorization code received"}, status=400)

#         # Correct the request data to include the right grant_type
#         data = {
#             "grant_type": "authorization_code",  # Correct grant_type for authorization code flow
#             "code": auth_code,                   # The authorization code received
#             "redirect_uri": PONTO_REDIRECT_URI ,
#         }
#         clientID = 'bb85a9ef-c106-4646-a53e-c8f405639208'
#         clientSecret = 'b89c0430-0823-47b0-a400-e7501e8ce4d4'
#         client = convertclientidsecret(clientID,clientSecret)
#         headers = {
#             "Content-Type": "application/x-www-form-urlencoded",
#             "Accept": "application/vnd.api+json",
#             "Authorization": f"Basic {client}"
#         }
#         data = {
#             "grant_type": "authorization_code",
#             "code": "Mc_2aWJc0G6OnlFib2m5zuGzOcoQwOTvQ_OR8CAEwDg.J9kNgQA_tNmo5FXr-mTzvDxdXPTyGCTufGZaHtLCGfk",
#             "client_id": "bb85a9ef-c106-4646-a53e-c8f405639208",
#             "redirect_uri": "http:127.0.0.1:8003/api/ponto-login/",
#             "code_verifier": "bbe4d91ae3cf8e88ba4341c5a8202896d3d6002cfd2042d606"
#         }
#         print(data,'data')
#         # Send the request to the token URL
#         # Full path to the certificate
#         certificate_path = r"C:/Users/kunal\Downloads/application_bb85a9ef-c106-4646-a53e-c8f405639208/certificate.pem"
#         private_path= r"C:/Users/kunal\Downloads/application_bb85a9ef-c106-4646-a53e-c8f405639208/private_key.pem"

#         response = requests.post(
#             url,
#             headers=headers,
#             data=data,
#             cert=(certificate_path, private_path)  # Path to your cert and private key
#         )
#         password='Billify-2'
#         print('response',response)
#         print(f"Response status: {response.status_code}")
#         print(f"Response body: {response.text}")

#         if response.status_code == 200:
#             try:
#                 token_data = response.json()
#                 access_token = token_data.get("access_token")
#                 refresh_token = token_data.get("refresh_token")

#                 return Response({
#                     "access_token": access_token,
#                     "refresh_token": refresh_token
#                 })
#             except requests.exceptions.JSONDecodeError:
#                 return Response({"error": "Invalid JSON response from server"}, status=500)
#         else:
#             return Response({
#                 "error": "Failed to get access token",
#                 "details": response.text  # Log the raw response text instead of trying to parse it
#             }, status=500)
#     except Exception as e:
#         return Response({'message':str(e)})



# token_dir = "tokens"
# token_file_path = os.path.join(token_dir, "token.json")

# def get_access_token():
#     try:
#         with open(token_file_path, "r") as file:
#             token_data = json.load(file)
#             return token_data["access_token"]
#     except (FileNotFoundError, KeyError):
#         print("Error: Token file not found or invalid format.")
#         return None

# # Create your views here.
# def fetch_bank_accounts():
#     token = get_access_token()
#     headers = {"Authorization": f"Bearer {token}"}

#     response = requests.get(f"{API_BASE_URL}/accounts", headers=headers)

#     if response.status_code == 200:
#         accounts = response.json()["accounts"]
#         from .models import BankAccount

#         for acc in accounts:
#             obj, created = BankAccount.objects.update_or_create(
#                 account_id=acc["id"],
#                 defaults={
#                     "balance": acc["balance"]["amount"],
#                     "currency": acc["balance"]["currency"]
#                 }
#             )
#             print(f"Updated: {obj}")
#     else:
#         print("Failed to fetch accounts:", response.status_code, response.text)