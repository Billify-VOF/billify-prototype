from django.shortcuts import render
import os,json,requests
import requests
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect
from requests.auth import HTTPBasicAuth


from dotenv import load_dotenv
load_dotenv()


PONTO_CLIENT_ID = os.getenv('PONTO_CLIENT_ID')
PONTO_CLIENT_SECRET = os.getenv('PONTO_CLIENT_SECRET')
PONTO_AUTH_URL = os.getenv('PONTO_AUTH_URL')
PONTO_TOKEN_URL = os.getenv('PONTO_TOKEN_URL')
PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')


@api_view(['GET'])
def ponto_login(request):
    """
    Redirects the user to Ponto OAuth2 login page.
    """
    # auth_url = (f"{PONTO_AUTH_URL}?client_id={PONTO_CLIENT_ID}"
    #             f"&redirect_uri={PONTO_REDIRECT_URI}&response_type=code&scope=read")
    # print('auth_url',auth_url)
    auth_url= f"https://sandbox-authorization.myponto.com/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}&code_challenge={code_challenge}&code_challenge_method={challenge_method}&onboarding_details_id={onboarding_details_id}&language={language}"
    return redirect(auth_url)

@api_view(['GET'])
def ponto_callback(request):
    """
    Handles Ponto callback and exchanges authorization code for access token.
    """
    auth_code = request.GET.get('code')

    if not auth_code:
        return Response({"error": "No authorization code received"}, status=400)

    # Exchange auth code for access token
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": PONTO_REDIRECT_URI
    }

    response = requests.post(
        PONTO_TOKEN_URL,
        data=data,
        auth=HTTPBasicAuth(PONTO_CLIENT_ID, PONTO_CLIENT_SECRET)
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        return Response({
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    else:
        return Response({"error": "Failed to get access token", "details": response.json()}, status=400)


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