"""Token management views for Ponto integration."""
import json
import logging
import ssl

# Third-party imports
import certifi
import urllib3
from urllib.parse import urlencode

# Django imports
from django.shortcuts import redirect
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response

# Local imports
from infrastructure.django.repositories.ponto_repository import DjangoIbanityAccountRepository, DjangoPontoTokenRepository
from domain.services.ponto_service import IbanityAccountService, PontoTokenService
from integrations.providers.ponto import PontoProvider
from typing import Dict, Any

from config.settings.base import LOG_LEVEL, PONTO_CLIENT_ID, PONTO_CLIENT_SECRET, \
    PONTO_AUTH_URL, PONTO_REDIRECT_URI, PONTO_CONNECT_BASE_URL

# Configure logger
logger = logging.getLogger(__name__)
# Get log level from environment variable with a default of INFO
try:
    logger.setLevel(getattr(logging, LOG_LEVEL))
except AttributeError:
    logger.warning(f"Invalid log level '{LOG_LEVEL}', defaulting to INFO")
    logger.setLevel(logging.INFO)

class PontoView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject dependencies
        self.ibanityAccountRepository = DjangoIbanityAccountRepository()
        self.ibanityAccountService = IbanityAccountService(
            ibanityAccountRepository=self.ibanityAccountRepository
        )
        self.pontoTokenRepository = DjangoPontoTokenRepository()
        self.pontoTokenService = PontoTokenService(pontoTokenRepository=self.pontoTokenRepository)

    def fetch_account_details(self, request):
        """Fetches account details for the authenticated user from the Ponto Connect API.

        This endpoint retrieves account details for the authenticated user by making a request to the
        Ponto Connect API. It requires the user to be authenticated and have a valid access token.
        The response includes account data, which is also saved or updated in the local database.

        Endpoint:
            GET /api/ponto/accounts/

        Authentication:
            - SessionAuthentication (User must be authenticated)

        Permissions:
            - IsAuthenticated

        Returns:
            Response: JSON response containing the account details or an error message.
        """
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
            
        user = request.user
        token = self.pontoTokenService.get_access_token(user)
        
        if not token:
            return Response({"error": "No access token found for user"}, status=404)

        # Create the signature
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create an SSL context with the private key password
        context = PontoProvider.create_ssl_context()

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
                f"{PONTO_CONNECT_BASE_URL}accounts?page[limit]=3",
                headers=headers
            )
            accounts_data = json.loads(response.data.decode('utf-8'))
            
            # Check if the accounts data contains any accounts
            if not accounts_data.get('data'):
                return Response({"error": "No accounts found"}, status=404)

            accountData = self.ibanityAccountService.add_or_update(user, accounts_data)
            
            if isinstance(accountData, dict) and "error" in accountData:
                return Response(accountData, status=500)
                
            return Response(accountData)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response for user {user}: {str(e)}")
            return Response({"error": f"Invalid JSON response: {e}"}, status=500)
        except urllib3.exceptions.HTTPError as e:
            logger.error(f"HTTP error while fetching account details for user {user}: {str(e)}")
            return Response({"error": f"HTTP request failed: {e}"}, status=500)
        except Exception as e:
            logger.error(f"Error occurred while fetching account details for user {user}: {str(e)}")
            return Response({"error": f"Request failed: {e}"}, status=500)


    def ponto_login(self, request: HttpRequest) -> Response:
        """
        Handles both the redirection to Ponto's OAuth2 login page and the callback
        to exchange the authorization code for an access token.
        
        Args:
            request: The HTTP request.
            
        Returns:
            Response: The redirect or token response.
        """
        session_id = PontoProvider.generate_random_session_id()
        auth_url = (
            f"{PONTO_AUTH_URL}?"
            f"client_id={PONTO_CLIENT_ID}&"
            f"redirect_uri={PONTO_REDIRECT_URI}&"
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
            client = PontoProvider.generate_client_credentials(PONTO_CLIENT_ID, PONTO_CLIENT_SECRET)
            
            # Prepare request data for the token exchange
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/vnd.api+json",
                "Authorization": f"Basic {client}"
            }
            
            data = {
                "grant_type": "authorization_code", 
                "code": auth_code,                  
                "redirect_uri": PONTO_REDIRECT_URI,
            }
            
            encoded_data = urlencode(data).encode('utf-8')
            # Create a PoolManager with the SSL context
            context = PontoProvider.create_ssl_context()
            
            http = urllib3.PoolManager(
                num_pools=50,
                cert_reqs=ssl.CERT_REQUIRED,
                ca_certs=certifi.where(),
                ssl_context=context
            )
            
            response = http.request(
                'POST',
                PONTO_CONNECT_BASE_URL,
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
                    encrypted_access_token = PontoProvider.encrypt_token(access_token)
                    encrypted_refresh_token = PontoProvider.encrypt_token(refresh_token)
                    self.pontoTokenService.add_or_update(user=user, data={
                        'access_token': encrypted_access_token,
                        'refresh_token': encrypted_refresh_token,
                        'expires_in': expires_in,
                    })
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

    def refresh_access_token(self, request: HttpRequest):
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
            ponto_token = self.pontoTokenService.get(user=user)
            if not ponto_token.refresh_token:
                return Response({"error": "Refresh token not found"}, status=400)
            # Decrypt the stored refresh token
            decrypted_refresh_token = PontoProvider.decrypt_token(ponto_token.refresh_token)
            # Prepare request data for refreshing the token
            client = PontoProvider.generate_client_credentials(PONTO_CLIENT_ID, PONTO_CLIENT_SECRET)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/vnd.api+json",
                "Authorization": f"Basic {client}"
            }
            data = {
                "grant_type": "refresh_token",
                "refresh_token": decrypted_refresh_token,
                "client_id": PONTO_CLIENT_ID,
            }
            encoded_data = urlencode(data).encode('utf-8')

            # Set up SSL context for cert and key
            context = PontoProvider.create_ssl_context()

            http = urllib3.PoolManager(
                num_pools=50,
                cert_reqs=ssl.CERT_REQUIRED,
                ca_certs=certifi.where(),
                ssl_context=context
            )

            response = http.request(
                'POST',
                PONTO_CONNECT_BASE_URL,
                headers=headers,
                body=encoded_data,
                preload_content=True
            )

            if response.status == 200:
                token_data: Dict[str, Any] = json.loads(response.data.decode('utf-8'))
                encrypted_access_token = PontoProvider.encrypt_token(token_data.get("access_token"))
                encrypted_refresh_token = PontoProvider.encrypt_token(token_data.get("refresh_token", decrypted_refresh_token))
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
        except Exception as e:
            logger.error(f"User {user} - Error occurred: {str(e)}")
            return Response({"error": str(e)}, status=500)

    # Get transaction History
    def get_transaction_history(self, request: HttpRequest):
        """Get transaction history for a user's account.
        
        Args:
            request: The HTTP request.
            
        Returns:
            Response: The transaction history data.
        """
        try:
            user = request.user.id
            try:
                token = self.pontoTokenService.get_access_token(user)
            except ValueError as e:
                return Response({"error": f"Invalid token: {str(e)}"}, status=400)
            except Exception as e:
                logger.error(f"Error retrieving access token: {str(e)}")
                return Response({"error": "Failed to retrieve access token"}, status=500)

            ibanityAccount = self.ibanityAccountService.get(user=user)
            if not ibanityAccount:
                return Response({"error": "No Ibanity account found for this user"}, status=404)
            account_id = ibanityAccount.account_id
            api_url = f"{PONTO_CONNECT_BASE_URL}accounts/{account_id}/transactions"

            # Create the request headers
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create an SSL context with the private key password
            context = PontoProvider.create_ssl_context()

            # Create a PoolManager with the SSL context
            http = urllib3.PoolManager(
                num_pools=50,
                cert_reqs=ssl.CERT_REQUIRED,  
                ca_certs=certifi.where(),
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
        except Exception as e:
            logger.error(f"Unhandled exception in get_transaction_history: {str(e)}")
            return Response({"error": f"Request failed: {str(e)}"}, status=500)
